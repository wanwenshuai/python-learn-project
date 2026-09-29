"""
===== 第20课：日志与日期时间 =====
对标 Java 的 slf4j/logback 和 java.time
"""

print('⚠️ 本课会故意触发若干异常用于教学演示，它们都会被 try/except 捕获，控制台出现 Error / Exception 字样属正常现象，脚本退出码为 0\n')

import calendar
import logging
import logging.config
import logging.handlers
import shutil
import sys
import time
import warnings
from datetime import date, datetime, time as dtime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

# 演示用日志目录（脚本结尾会整个删除）
LOG_DIR = Path("demo_logs")
LOG_DIR.mkdir(exist_ok=True)


def reset_root_logger() -> None:
    """
    清空 root logger 上的所有 handler（教学演示专用）。

    Java: LoggerContext 里 reset 掉 root logger 的 appender 列表
    作用：让本文件每一段日志演示互不干扰。
    """
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        handler.close()


def close_all_handlers() -> None:
    """
    关闭所有 logger 上的 handler，释放文件句柄（≈ logback 的 context.stop()）。

    不关的话日志文件可能还被进程占着，删除时会出问题（Windows 上尤其明显）。
    """
    all_loggers = [logging.getLogger()]
    for obj in logging.Logger.manager.loggerDict.values():
        if isinstance(obj, logging.Logger):
            all_loggers.append(obj)
    for logger_obj in all_loggers:
        for handler in logger_obj.handlers[:]:
            logger_obj.removeHandler(handler)
            handler.close()


# ==================== 一、为什么不用 print ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
#
# print 的五个致命伤（对照 Java 的 System.out.println vs logger.info）：
#   1. 无法分级      —— 生产环境要按级别过滤，print 全部混在一起
#   2. 无法关闭      —— 上线后想去掉调试输出？只能删代码重新打包
#   3. 无时间戳      —— 出故障时不知道日志是什么时候打的
#   4. 无调用位置    —— 不知道是哪个类哪一行打的
#   5. 无法输出到文件 —— logback 一个配置就能同时输出到控制台 + 文件 + Kafka
#
# 企业规范：业务代码禁止 print，统一用 logger。
# 唯一的例外：命令行工具的纯结果输出（stdout 就是产品的一部分时）。

print("【print 方式】用户 alice 登录成功")
# 输出值: 【print 方式】用户 alice 登录成功
# 问题：没有级别、没有时间、没有位置，上线后想关掉只能改代码

# 说明：logging 默认把日志写到 stderr（标准错误流）。
# 为了让本文件在终端里的输出顺序稳定可读，这里先把 root 的输出流显式指向 stdout。
# 真实项目不需要这行 —— stderr 更规范，业务流和错误流分离，方便运维分别采集。
logging.basicConfig(stream=sys.stdout)

# ==================== 二、五个日志级别 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
#
# Python 的 5 个级别（数值越大越严重）：
#   DEBUG(10) < INFO(20) < WARNING(30) < ERROR(40) < CRITICAL(50)
#
# 对照 slf4j（logback）：
#   slf4j:  TRACE   DEBUG   INFO   WARN    ERROR
#   Python: (无)    DEBUG   INFO   WARNING ERROR   CRITICAL
#   注意两点：Python 没有 TRACE；Python 叫 WARNING 且多了一个 CRITICAL
#
# 最关键的一条：root logger 的默认级别是 WARNING，
# 所以不配置的话 DEBUG / INFO 打出来什么都看不见（新手第一大坑）。

logging.debug("这是一条 DEBUG 日志")       # 默认级别下不显示，这行什么都不输出
logging.info("这是一条 INFO 日志")         # 默认级别下不显示，这行什么都不输出
logging.warning("这是一条 WARNING 日志")
# 输出值: WARNING:root:这是一条 WARNING 日志
logging.error("这是一条 ERROR 日志")
# 输出值: ERROR:root:这是一条 ERROR 日志
logging.critical("这是一条 CRITICAL 日志")
# 输出值: CRITICAL:root:这是一条 CRITICAL 日志
# 上面三行的格式 LEVEL:name:message 是 logging 的默认格式（BASIC_FORMAT）

# 用 setLevel 调整级别：调到 DEBUG 后，DEBUG 及以上全部输出
logging.getLogger().setLevel(logging.DEBUG)
logging.debug("调低级别后，DEBUG 也能输出了")
# 输出值: DEBUG:root:调低级别后，DEBUG 也能输出了

# 级别的实际含义（企业项目约定）：
#   DEBUG    —— 开发调试细节，参数值、分支走向，生产环境关闭
#   INFO     —— 关键业务流程节点，如"订单创建成功 orderId=123"，生产环境保留
#   WARNING  —— 不影响主流程但需要关注，如"缓存未命中，回源查询"
#   ERROR    —— 业务失败但服务还活着，如"调用支付网关失败"，必须告警
#   CRITICAL —— 服务不可用，如"数据库连接池耗尽"，必须电话告警

# ==================== 三、basicConfig 快速配置 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
#
# Java 对照：相当于用代码代替 logback.xml 做最小配置。
# 常用参数：
#   level     —— root logger 的级别
#   format    —— 输出格式字符串
#   datefmt   —— %(asctime)s 的格式（strftime 语法，见本课第二部分）
#   filename  —— 指定后输出到文件而不是控制台
#   filemode  —— 'a' 追加（默认）/ 'w' 覆盖，类比 logback 的 append 属性
#   encoding  —— 强烈建议写 utf-8，否则中文在 Windows 上会乱码
#   stream    —— 输出流，默认 sys.stderr
#
# 常用 format 字段：
#   %(asctime)s   时间        %(levelname)s 级别名
#   %(name)s      logger 名   %(message)s   日志内容
#   %(lineno)d    行号        %(funcName)s  函数名
#   %(module)s    模块名      %(process)d   进程号
#   %(threadName)s 线程名

reset_root_logger()          # 先清掉上面自动加的 handler，否则 basicConfig 不生效

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logging.debug("basicConfig 之后 DEBUG 也能输出了")
# 输出示例: 2026-09-20 10:30:00 [DEBUG] root - basicConfig 之后 DEBUG 也能输出了
# 格式含义：时间 [级别] logger名 - 内容

# logback 常见 pattern 的 Python 等价写法：
#   logback: %d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n
#   Python : "%(asctime)s [%(threadName)s] %(levelname)s %(name)s - %(message)s"
#            datefmt="%Y-%m-%d %H:%M:%S"
# Python 的 datefmt 不支持毫秒写法（%f 只在 strftime 里有效，asctime 走的是 time.strftime），
# 需要毫秒时用自定义 Formatter + datetime 格式化（本课第四节给了写法）。

# ⚠️ 坑1：basicConfig 只在 root logger 还没有 handler 时才生效，重复调用是空操作
#         可以用 force=True 强制重配（Python 3.8+）
logging.basicConfig(level=logging.ERROR, format="%(message)s", stream=sys.stdout)
logging.info("第二次 basicConfig 没生效：级别还是 DEBUG，INFO 照样输出")
# 输出示例: 2026-09-20 10:30:00 [INFO] root - 第二次 basicConfig 没生效：级别还是 DEBUG，INFO 照样输出

# ⚠️ 坑2：basicConfig(filename=...) 之后日志只进文件，控制台一条都没有
reset_root_logger()
logging.basicConfig(
    filename=str(LOG_DIR / "basic.log"),
    filemode="a",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.info("这条日志写进了文件，控制台看不到")
print("basic.log 存在:", (LOG_DIR / "basic.log").exists())
# 输出值: basic.log 存在: True

# ==================== 四、Logger / Handler / Formatter 三件套 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
#
# 这是 logging 的核心架构，和 logback 一一对应：
#
#   Python              logback              职责
#   ------------------  -------------------  ------------------------------
#   Logger              Logger               产生日志、判断级别
#   Handler             Appender             决定日志去哪儿（控制台/文件/网络）
#   Formatter           Encoder/Layout       决定日志长什么样
#
# 一条日志的流转（和 logback 完全一致）：
#   logger.info(msg)
#     -> logger 判断 msg 级别 >= 自己的有效级别？不够直接丢弃
#     -> 构造 LogRecord
#     -> 交给自己的每个 Handler（每个 Handler 还有自己的级别，再过滤一次）
#     -> Handler 用 Formatter 格式化后写出
#     -> 如果 propagate=True，同一份 LogRecord 继续往父 logger 传

reset_root_logger()          # 保证 root 没有 handler，排除干扰


def init_logger(name: str, level: int = logging.INFO, log_file: str | None = None) -> logging.Logger:
    """
    生产可用的 logger 初始化函数（等价于一份精简的 logback.xml）。

    Java 对照：
        Logger logger = LoggerFactory.getLogger(XxxService.class);
        + logback.xml 里的 appender / encoder 配置

    :param name:     logger 名称，模块内固定用 __name__
    :param level:    日志级别
    :param log_file: 需要同时落文件时传文件路径，不需要则传 None
    :return:         配置好的 Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # propagate=False：不再把日志冒泡给父 logger，这是避免"日志打印两遍"的关键
    logger.propagate = False
    # 幂等保护：已经配置过就直接返回，防止重复 addHandler 导致日志翻倍
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s [%(funcName)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


app_logger = init_logger("demo.app", logging.INFO)
app_logger.info("订单创建成功 orderId=%s", "A1001")
# 输出示例: 2026-09-20 10:30:00 [INFO] demo.app [<module>:行号] - 订单创建成功 orderId=A1001
# 格式含义：时间 [级别] logger名 [函数名:行号] - 内容
# 行号随代码修改会变，所以这里标"输出示例"；funcName 是 <module> 表示在模块顶层直接调用
app_logger.debug("这条 DEBUG 被级别过滤掉了，不会输出")

# === getLogger(__name__) 的模块级惯例 ===
# Java 里每个类写：private static final Logger log = LoggerFactory.getLogger(XxxService.class);
# Python 里每个模块写：logger = logging.getLogger(__name__)
#
# 为什么用 __name__ 而不是普通字符串？
#   1. __name__ 是模块的完整导入路径，如 "myapp.service.order"
#      于是 logger 名字天然形成树形层级，和 Java 用类全限定名做 logger 名一个道理
#   2. 层级带来"继承"能力：把 "myapp" 级别调成 DEBUG，整个应用都跟着变
#   3. 跨模块不会重名冲突，日志里一眼看出是哪个模块打的
module_logger = logging.getLogger(__name__)
print("本模块的 logger 名 =", __name__)
# 输出值: 本模块的 logger 名 = __main__
# 注意：直接运行脚本时 __name__ 是 "__main__"；被 import 时才是模块名（如 "myapp.order"）

# === propagate：日志重复打印的根因 ===
# 子 logger 处理完自己的 handler 后，默认还会把同一条 LogRecord 向上冒泡给父 logger，
# 父 logger 的 handler 再输出一次 —— 这就是"日志打了两遍"的经典原因。
parent_logger = logging.getLogger("demo.prop")
parent_logger.setLevel(logging.INFO)
parent_logger.propagate = False          # 阻断冒泡到 root
parent_handler = logging.StreamHandler(sys.stdout)
parent_handler.setFormatter(logging.Formatter("父 logger 输出 -> %(message)s"))
parent_logger.addHandler(parent_handler)

child_logger = logging.getLogger("demo.prop.child")
child_logger.setLevel(logging.INFO)
child_handler = logging.StreamHandler(sys.stdout)
child_handler.setFormatter(logging.Formatter("子 logger 输出 -> %(message)s"))
child_logger.addHandler(child_handler)

child_logger.info("演示日志冒泡")
# 输出值: 子 logger 输出 -> 演示日志冒泡
# 输出值: 父 logger 输出 -> 演示日志冒泡
# 两条！同一条日志被子 logger 和父 logger 各输出了一遍

child_logger.propagate = False           # 关闭冒泡（生产环境推荐）
child_logger.info("关闭 propagate 后")
# 输出值: 子 logger 输出 -> 关闭 propagate 后
# 现在只有一条了

# 结论：自定义 logger 要么 propagate=False，要么保证父/root logger 不挂 handler，
#       两者占其一，否则日志必然重复。

# ==================== 五、输出到文件与轮转 ====================
# ⭐⭐ 常用 —— 经常用
#
# Java 对照：logback 的 FileAppender / RollingFileAppender
#   FileHandler              ≈ FileAppender
#   RotatingFileHandler      ≈ RollingFileAppender（按大小轮转）
#   TimedRotatingFileHandler ≈ RollingFileAppender + TimeBasedRollingPolicy（按时间轮转）

# === FileHandler：最简单的文件输出 ===
file_logger = logging.getLogger("demo.file")
file_logger.setLevel(logging.INFO)
file_logger.propagate = False
plain_handler = logging.FileHandler(LOG_DIR / "plain.log", mode="a", encoding="utf-8")
plain_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
file_logger.addHandler(plain_handler)
file_logger.info("写进 plain.log")
print("plain.log 存在:", (LOG_DIR / "plain.log").exists())
# 输出值: plain.log 存在: True

# === RotatingFileHandler：按大小轮转 ===
# maxBytes：单个文件上限，超过就切成 .1 .2 ...；backupCount：保留几个历史文件
# Java: <rollingPolicy class="ch.qos.logback.core.rolling.FixedWindowRollingPolicy">
#       <maxFileSize>10MB</maxFileSize><maxHistory>5</maxHistory>
rotate_logger = logging.getLogger("demo.rotate")
rotate_logger.setLevel(logging.INFO)
rotate_logger.propagate = False
rotate_handler = logging.handlers.RotatingFileHandler(
    LOG_DIR / "rotate.log", maxBytes=300, backupCount=2, encoding="utf-8"
)
rotate_handler.setFormatter(logging.Formatter("%(message)s"))
rotate_logger.addHandler(rotate_handler)
for i in range(20):
    rotate_logger.info("这条日志用来撑大文件体积，触发按大小轮转，序号=%d", i)
rotate_handler.close()
print("轮转后文件名:", sorted(p.name for p in LOG_DIR.glob("rotate.log*")))
# 输出值: 轮转后文件名: ['rotate.log', 'rotate.log.1', 'rotate.log.2']
# rotate.log 是最新的，.1 次新，.2 最旧；backupCount=2 表示只留 2 个历史文件，再老的就删了

# === TimedRotatingFileHandler：按时间轮转 ===
# when：S 秒 / M 分 / H 小时 / D 天 / midnight 每天零点 / W0-W6 每周几
# interval：间隔几个单位；backupCount：保留几个历史文件
# Java: <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
#       <fileNamePattern>app.%d{yyyy-MM-dd}.log</fileNamePattern>
timed_logger = logging.getLogger("demo.timed")
timed_logger.setLevel(logging.INFO)
timed_logger.propagate = False
timed_handler = logging.handlers.TimedRotatingFileHandler(
    LOG_DIR / "timed.log", when="S", interval=1, backupCount=2, encoding="utf-8"
)
timed_handler.setFormatter(logging.Formatter("%(message)s"))
timed_logger.addHandler(timed_handler)
timed_logger.info("轮转前的日志")
timed_handler.doRollover()               # 手动强制轮转一次（真实项目由时间自动触发）
timed_logger.info("轮转后的日志")
timed_handler.close()
print("轮转后文件数:", len(list(LOG_DIR.glob("timed.log*"))))
# 输出值: 轮转后文件数: 2
# 一个是 timed.log（当前），一个是 timed.log.2026-09-20_10-30-00 这种带时间戳的历史文件
# 历史文件名带时间戳，无法预测，所以这里只数个数

# ==================== 六、日志格式化的正确姿势 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
#
# ✅ 推荐：logger.info("用户 %s 登录", username)
# ❌ 避免：logger.info(f"用户 {username} 登录")
#
# 原因：惰性求值。%s 写法把参数原样传进去，只有真的要输出时才做字符串格式化；
#       f-string 是在调用 logger 之前就把字符串拼好了，级别不够（不输出）时纯属白干活。
#       slf4j 的 log.info("user {} login", username) 是同一个设计思想，原因完全一致。
#
# 什么时候 f-string 也可以接受？
#   1. 你确定这条日志一定会输出（级别够高，比如 error 级别）
#   2. 参数拼装逻辑复杂，%s 写法可读性明显变差
#   3. 参数不是对象而是需要调用方法才能拿到值（此时两种写法都会求值，没区别）


class User:
    """用来观察"到底什么时候发生了字符串格式化"的探针类"""

    def __str__(self) -> str:
        print("   >>> 发生了格式化：User.__str__ 被调用")
        return "alice"


fmt_logger = init_logger("demo.fmt", logging.INFO)   # 只输出 INFO 及以上
user = User()

# ✅ 正确：%s 占位符 + 参数分开传
fmt_logger.info("正确写法：用户 %s 登录", user)
# 输出值:    >>> 发生了格式化：User.__str__ 被调用
# 输出示例: 2026-09-20 10:30:00 [INFO] demo.fmt [<module>:行号] - 正确写法：用户 alice 登录
# 注意顺序：格式化发生在写日志之前，所以先看到探针那行，再看到日志本身

# ✅ 正确：级别不够，直接丢弃，连 __str__ 都不会被调用（零开销）
fmt_logger.debug("正确写法：用户 %s 登录", user)
# 这行什么都不输出，上面那句 ">>> 发生了格式化" 也不会再出现 —— 这就是惰性求值

# ❌ 错误：f-string 在调用 logger 之前就执行了，日志一条没打，活却干完了
fmt_logger.debug(f"错误写法：用户 {user} 登录")
# 输出值:    >>> 发生了格式化：User.__str__ 被调用
# 注意：日志没输出，但格式化照样发生了 —— 生产环境高频调用时会白白消耗 CPU

# ==================== 七、异常日志 ====================
# ⭐⭐ 常用 —— 经常用
#
# Java: log.error("下单失败", e);            // 第二个参数传异常对象，自动打堆栈
# Python: logger.exception("下单失败")       // 自动附带完整堆栈
#         logger.error("下单失败", exc_info=True)   // 完全等价，显式写法
#
# 区别：exception() 只能在 except 块里用（它靠 sys.exc_info() 拿当前异常），
#       在 except 外面用会打不出堆栈。error(exc_info=True) 同理。

exc_logger = init_logger("demo.exc", logging.INFO)


def divide(a: int, b: int) -> float:
    """一个会抛真实异常的函数"""
    return a / b


print("\n⚠️ 下面这段 Traceback 是【故意触发】的教学演示：异常已被 except 捕获，程序不会退出，脚本退出码仍是 0\n")
try:
    divide(10, 0)
except ZeroDivisionError:
    exc_logger.exception("计算失败，入参 a=%s b=%s", 10, 0)
    # 输出示例（第一行是日志，后面是自动附带的堆栈）:
    # 2026-09-20 10:30:00 [ERROR] demo.exc [<module>:行号] - 计算失败，入参 a=10 b=0
    # Traceback (most recent call last):
    #   File ".../20_logging_datetime.py", line 3xx, in <module>
    #     divide(10, 0)
    #   File ".../20_logging_datetime.py", line 3xx, in divide
    #     return a / b
    # ZeroDivisionError: division by zero
    # 要点1：堆栈是 logging 自动追加到消息后面的，format 里不需要写 %(exc_info)s
    # 要点2：堆栈里那段 ~~~~^^^ 是 Python 3.11+ 的细粒度错误定位，直接指出出错的具体运算

# 等价写法：显式传 exc_info=True
print("\n⚠️ 下面这段同样是【故意触发】的演示，不是程序报错\n")
try:
    divide(1, 0)
except ZeroDivisionError:
    exc_logger.error("等价写法：显式 exc_info=True", exc_info=True)

print("⚠️ 堆栈演示结束 —— 上面两段 Traceback 是 logging 的正常输出内容，脚本已继续往下执行\n")
    # 输出示例: 2026-09-20 10:30:00 [ERROR] demo.exc [<module>:行号] - 等价写法：显式 exc_info=True
    #           Traceback (most recent call last): ... 后续堆栈与上面完全一致

# 生产建议：异常日志必须带上下文参数（订单号、用户 ID、入参），
#           否则线上排查时只知道"报了个空指针"，不知道是谁的请求。
#           注意别把密码、身份证号、token 打进日志 —— 合规红线。

# ==================== 八、配置字典 dictConfig ====================
# ⭐ 了解 —— 用到再查
#
# Java 对照：dictConfig 就是"用 Python 字典写一份 logback.xml"。
# 生产项目通常从 YAML/JSON 文件读进来再 dictConfig，不在代码里硬编码 —— 改日志级别不用重新打包。
#
# 结构对照：
#   logback.xml                    dictConfig
#   ----------------------------   ------------------------------
#   <appender>                     "handlers"
#   <encoder><pattern>             "formatters"
#   <logger name="..." level="..."> "loggers"
#   <root level="...">             "root"
#   <logger additivity="false">    "propagate": False
#   scan="true"（热加载）           ｜ Python 不支持，需自己写文件监听
#
# class 字段的值格式是 "模块路径.类名"，也可以写 "ext://sys.stdout" 这种外部对象引用。

LOGGING_CONFIG = {
    "version": 1,                                   # 固定写 1，配置格式版本号
    "disable_existing_loggers": False,              # 关键：别把已创建的 logger 禁用了
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s - %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "stream": "ext://sys.stdout",           # 引用 sys.stdout 对象
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "WARNING",                     # 文件里只留 WARNING 以上，减少体积
            "formatter": "standard",
            "filename": str(LOG_DIR / "dict_config.log"),
            "maxBytes": 10 * 1024 * 1024,           # 10MB
            "backupCount": 3,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        # 只配置 "demo.dict" 这个 logger，其它模块不受影响
        "demo.dict": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
    "root": {"level": "WARNING", "handlers": ["console"]},
}

reset_root_logger()                 # 清掉前面手动加的 handler，演示干净的效果
logging.config.dictConfig(LOGGING_CONFIG)

dict_logger = logging.getLogger("demo.dict")
dict_logger.debug("DEBUG 进控制台（handler 级别是 DEBUG）")
# 输出示例: 2026-09-20 10:30:00 [DEBUG] demo.dict - DEBUG 进控制台（handler 级别是 DEBUG）
dict_logger.warning("WARNING 同时进控制台和文件")
# 输出示例: 2026-09-20 10:30:00 [WARNING] demo.dict - WARNING 同时进控制台和文件
print("dict_config.log 存在:", (LOG_DIR / "dict_config.log").exists())
# 输出值: dict_config.log 存在: True
print("dict_config.log 行数:", len((LOG_DIR / "dict_config.log").read_text(encoding="utf-8").strip().splitlines()))
# 输出值: dict_config.log 行数: 1
# 只有 WARNING 那一条进了文件 —— DEBUG 被 file handler 自己的级别挡住了
# 这印证了第四节说的：logger 过滤一次，每个 handler 还会各自再过滤一次

# ==================== 九、四个核心类 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
#
# 关系图（注释版）：
#
#        date           time
#     (年 月 日)      (时 分 秒 微秒)
#          \            /
#           \          /
#            datetime            ≈ date + time 的组合体，最常用
#                |
#                |  两个 datetime 相减
#                v
#            timedelta           时间间隔（≈ Java 的 Duration + Period 合体）
#
# Java 对照表：
#   java.time.LocalDate        <->  datetime.date       只有日期
#   java.time.LocalTime        <->  datetime.time       只有时间
#   java.time.LocalDateTime    <->  datetime.datetime   日期 + 时间
#   java.time.Duration/Period  <->  datetime.timedelta  时间间隔
#
# 不可变性：这三兄弟全部是不可变对象，任何运算都返回新对象，原对象纹丝不动 —— 和 java.time 一致。
# 对比老的 java.util.Date：可变（setTime 会改自己）、月份从 0 开始、还混着时区，设计很混乱。
# Python 的 datetime 从诞生起就是不可变设计，没走过 java.util.Date 那条弯路。

d = date(2024, 3, 15)
t = dtime(14, 30, 45)
dt = datetime(2024, 3, 15, 14, 30, 45)
delta = timedelta(days=1, hours=2, minutes=30)

print(d)
# 输出值: 2024-03-15
print(t)
# 输出值: 14:30:45
print(dt)
# 输出值: 2024-03-15 14:30:45
print(delta)
# 输出值: 1 day, 2:30:00
print(dt.date())
# 输出值: 2024-03-15
print(dt.time())
# 输出值: 14:30:45
print(datetime.combine(d, t))
# 输出值: 2024-03-15 14:30:45

# 取值：属性直接访问（Java 是 getYear() / getMonthValue() 方法）
print(dt.year, dt.month, dt.day)
# 输出值: 2024 3 15
print(dt.hour, dt.minute, dt.second, dt.microsecond)
# 输出值: 14 30 45 0

# 不可变性验证：replace 返回新对象，原对象不变
new_dt = dt.replace(year=2025)
print(new_dt)
# 输出值: 2025-03-15 14:30:45
print(dt)
# 输出值: 2024-03-15 14:30:45
# 原对象还是 2024 年 —— 想改就得接收返回值，没有 setYear() 这种原地修改的方法

# ==================== 十、获取当前时间 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
#
# Java 对照：
#   LocalDateTime.now()      <->  datetime.now()            本地时间，naive（不带时区）
#   LocalDate.now()          <->  date.today()
#   ZonedDateTime.now(zone)  <->  datetime.now(timezone.utc) aware（带时区）
#
# ⚠️ 最坑的概念：naive（天真）vs aware（带时区）
#   naive：只有日期时间数字，不带 tzinfo，含义完全取决于"读者假设的时区"—— 跨时区就是灾难
#   aware：带 tzinfo，能明确算出 UTC 时刻，能安全地做时区转换和跨时区比较
#   规则：涉及存储、传输、跨时区，一律用 aware；纯本地的展示层可以用 naive

now = datetime.now()
today = date.today()
now_utc = datetime.now(timezone.utc)

print(now)
# 输出示例: 2026-09-20 10:30:00.123456
# 格式含义：年-月-日 时:分:秒.微秒，本地时区，末尾没有 +08:00 之类 —— 说明是 naive
print(today)
# 输出示例: 2026-09-20
print(now_utc)
# 输出示例: 2026-09-20 02:30:00.123456+00:00
# 末尾 +00:00 说明是 aware，时区是 UTC
print("now 的时区:", now.tzinfo)
# 输出值: now 的时区: None
print("now_utc 的时区:", now_utc.tzinfo)
# 输出值: now_utc 的时区: UTC
print("now_utc 的偏移:", now_utc.utcoffset())
# 输出值: now_utc 的偏移: 0:00:00

# ==================== 十一、格式化与解析 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
#
# strftime ：datetime -> 字符串（str format time）
# strptime ：字符串 -> datetime（str parse time）
#
# Java 对照：DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
# ⚠️ 格式符含义完全不同，别混：
#   Java  : yyyy-MM-dd HH:mm:ss.SSS     小写 y 是年，大写 MM 是月，大写 HH 是 24 小时
#   Python: %Y-%m-%d %H:%M:%S.%f        大写 %Y 是年，小写 %m 是月，%H 是 24 小时，%f 是微秒
#   记忆法：Python 全部带 % 前缀，年份是大写 Y 和小写 y 两种（4 位 / 2 位）
#
# 常用格式符：
#   %Y 四位年(2024)   %y 两位年(24)     %m 月(03)      %d 日(15)
#   %H 24小时制(14)   %I 12小时制(02)   %M 分(30)      %S 秒(45)
#   %f 微秒(123456)   %p AM/PM          %j 一年第几天(075)
#   %A 星期全名       %a 星期缩写       %B 月份全名    %b 月份缩写
#   %z 时区偏移       %Z 时区名
#
# 为了输出可预测，下面全部用固定的 datetime，不用 now()

FIXED = datetime(2024, 3, 15, 14, 30, 45, 123456)     # 2024-03-15 是星期五
FIXED_DATE = date(2024, 3, 15)

print(FIXED.strftime("%Y-%m-%d"))
# 输出值: 2024-03-15
print(FIXED.strftime("%Y-%m-%d %H:%M:%S"))
# 输出值: 2024-03-15 14:30:45
print(FIXED.strftime("%Y/%m/%d %H:%M:%S.%f"))
# 输出值: 2024/03/15 14:30:45.123456
print(FIXED.strftime("%y-%m-%d"))
# 输出值: 24-03-15
print(FIXED.strftime("%j"))
# 输出值: 075
print(FIXED.strftime("%A %a %B %b"))
# 输出值: Friday Fri March Mar
print(FIXED.strftime("%I:%M %p"))
# 输出值: 02:30 PM
print("naive 的 %z 输出:", repr(FIXED.strftime("%z")))
# 输出值: naive 的 %z 输出: ''
# 用 repr 才能看出是空字符串 —— naive 对象没有时区信息，%z 直接输出空串，又一处 naive 的坑

# Java 里日期格式化还得靠 DateTimeFormatter，Python 直接是对象的方法，更顺手
print(f"日期对象直接支持 f-string: {FIXED_DATE}")
# 输出值: 日期对象直接支持 f-string: 2024-03-15
# 因为 datetime 重写了 __format__，格式串里不写 % 前缀的普通文本也能正常输出

# === strptime：字符串解析成 datetime ===
parsed = datetime.strptime("2024-03-15 14:30:45", "%Y-%m-%d %H:%M:%S")
print(parsed)
# 输出值: 2024-03-15 14:30:45
print(type(parsed))
# 输出值: <class 'datetime.datetime'>
print(parsed.year, parsed.month, parsed.day)
# 输出值: 2024 3 15
# 解析出来就是普通 datetime 对象，属性和手工构造的完全一样

# 解析失败会抛 ValueError（不是返回 None，必须 try 包住）
try:
    datetime.strptime("2024/03/15", "%Y-%m-%d")
except ValueError as exc:
    print("解析失败:", exc)
# 输出值: 解析失败: time data '2024/03/15' does not match format '%Y-%m-%d'

# === ISO 8601 格式：跨系统传输的标准写法 ===
# Java 对照：ISO_LOCAL_DATE_TIME / LocalDateTime.parse("2024-03-15T14:30:45")
print(FIXED.isoformat())
# 输出值: 2024-03-15T14:30:45.123456
print(FIXED_DATE.isoformat())
# 输出值: 2024-03-15
print(datetime.fromisoformat("2024-03-15T14:30:45.123456"))
# 输出值: 2024-03-15 14:30:45.123456
print(datetime.fromisoformat("2024-03-15"))
# 输出值: 2024-03-15 00:00:00
print(datetime.fromisoformat("2024-03-15T14:30:45+08:00"))
# 输出值: 2024-03-15 14:30:45+08:00
# 建议：接口之间传时间一律用 ISO 8601（带时区更好），别自定义格式

# ==================== 十二、时间加减 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
#
# Java 对照：
#   dt.plusDays(1)                  <->  dt + timedelta(days=1)
#   dt.minusHours(2)                <->  dt - timedelta(hours=2)
#   ChronoUnit.MINUTES.between(a,b) <->  (b - a).total_seconds() / 60
#
# ⚠️ timedelta 的构造参数里没有"月"和"年"，也不支持毫秒这个单位名：
#   timedelta(days=, seconds=, microseconds=, milliseconds=, minutes=, hours=, weeks=)
#   要毫秒就写 milliseconds=500，或者自己算 microseconds=500_000

base = datetime(2024, 3, 15, 14, 30, 0)

print(base + timedelta(days=1))
# 输出值: 2024-03-16 14:30:00
print(base - timedelta(days=1))
# 输出值: 2024-03-14 14:30:00
print(base + timedelta(weeks=1))
# 输出值: 2024-03-22 14:30:00
print(base - timedelta(hours=2))
# 输出值: 2024-03-15 12:30:00
print(base + timedelta(milliseconds=500))
# 输出值: 2024-03-15 14:30:00.500000
print(base + timedelta(minutes=90))
# 输出值: 2024-03-15 16:00:00
# 90 分钟自动进位成 1 小时 30 分，timedelta 内部统一按 天/秒/微秒 归一化存储

# === 两个时间点相减，得到 timedelta ===
start = datetime(2024, 3, 15, 9, 0, 0)
end = datetime(2024, 3, 15, 18, 30, 0)
diff = end - start
print(diff)
# 输出值: 9:30:00
print(diff.days, diff.seconds, diff.microseconds)
# 输出值: 0 34200 0
# ⚠️ timedelta 只有 days/seconds/microseconds 三个分量，没有 hours/minutes 属性
#    seconds 是"去掉整天后剩余的秒数"，不是"总秒数"
print(diff.total_seconds())
# 输出值: 34200.0
print(diff.total_seconds() / 3600)
# 输出值: 9.5
# 想要小时/分钟数，一律用 total_seconds() 自己换算，别用 .seconds

# === timedelta 不支持按月/按年加减（和 Java 的 Period 不一样）===
# Java: date.plusMonths(1) 一行搞定
# Python: timedelta 没有 months 参数，因为"一个月"长度不固定（28~31 天）
print(datetime(2024, 1, 31) + timedelta(days=30))
# 输出值: 2024-03-01 00:00:00
# 本意想加"一个月"得到 2 月 31 日（不存在），结果算成了 3 月 1 日 —— 按天数硬加的结果

def add_months(source: datetime, months: int) -> datetime:
    """
    按月加减（≈ Java 的 plusMonths / minusMonths）。

    关键点：月末溢出要收敛到目标月的最后一天，
    例如 1 月 31 日加一个月，Java 的 plusMonths(1) 给 2 月 29 日（闰年），这里保持一致。

    :param source: 原始时间
    :param months: 要加的月数，负数表示减
    :return:       新的 datetime
    """
    total_month = source.month - 1 + months          # 转成 0 基的月份序号方便计算
    year = source.year + total_month // 12           # Python 的 // 是向下取整，负数也对
    month = total_month % 12 + 1
    last_day = calendar.monthrange(year, month)[1]   # 目标月最后一天是几号
    return source.replace(year=year, month=month, day=min(source.day, last_day))


print(add_months(datetime(2024, 1, 31), 1))
# 输出值: 2024-02-29 00:00:00
print(add_months(datetime(2024, 3, 31), -1))
# 输出值: 2024-02-29 00:00:00
print(add_months(datetime(2024, 12, 15), 2))
# 输出值: 2025-02-15 00:00:00
# 跨年也正确 —— 自己实现时最容易在跨年上翻车

# 第三方库 python-dateutil 的 relativedelta 更省事（需要 pip install python-dateutil）：
#   from dateutil.relativedelta import relativedelta
#   datetime(2024, 1, 31) + relativedelta(months=1)   # 2024-02-29 00:00:00
# 企业项目里凡是涉及"账单日""到期日"按月算的，都建议用它，别自己写。

# ==================== 十三、时间戳转换 ====================
# ⭐⭐ 常用 —— 经常用
#
# Java 对照：
#   instant.toEpochMilli()        <->  dt.timestamp() * 1000   （注意单位！）
#   Instant.ofEpochMilli(ms)      <->  datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
#
# ⚠️ 单位差异是经典事故点：
#   Java 的 Instant / System.currentTimeMillis() 是毫秒
#   Python 的 time.time() / datetime.timestamp() 是秒（float，带小数部分表示微秒）
#   前后端联调时看到 "1704067200" 而不是 "1704067200000"，八成就是这个原因。

epoch = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
print(epoch.timestamp())
# 输出值: 1704067200.0
# aware 对象的 timestamp() 结果与本地时区无关，永远准确

print(datetime.fromtimestamp(1704067200, tz=timezone.utc))
# 输出值: 2024-01-01 00:00:00+00:00
# 生产代码一律这样写：fromtimestamp + tz=timezone.utc

print(int(epoch.timestamp() * 1000))
# 输出值: 1704067200000
# 转成 Java 的毫秒时间戳

print(datetime.now(timezone.utc).timestamp())
# 输出示例: 1789000000.123456
# 当前时间的秒级时间戳，无法预测

# === 弃用警告：utcnow() / utcfromtimestamp() 在 3.12+ 已弃用 ===
# 老代码常见写法：
#   datetime.utcnow()                   # 弃用！返回的是 naive 对象，却被当成 UTC 用，极易出错
#   datetime.utcfromtimestamp(ts)       # 弃用！同样返回 naive
# 替代写法就是上面的 datetime.now(timezone.utc) / datetime.fromtimestamp(ts, tz=timezone.utc)
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")          # 强制捕获，避免直接打到终端污染输出
    legacy_utc = datetime.utcnow()
print("utcnow() 的返回值:", legacy_utc.tzinfo)
# 输出值: utcnow() 的返回值: None
print("utcnow() 触发的警告:", caught[0].category.__name__)
# 输出值: utcnow() 触发的警告: DeprecationWarning
# 看，返回的是 naive 对象（tzinfo 是 None）—— 这就是它被弃用的根本原因

# naive 的 timestamp() 按"本地时区"解释，这是另一个坑：
print(datetime(2024, 1, 1, 0, 0, 0).timestamp())
# 输出示例: 1704038400.0
# 本机在 UTC+8 时得到的是 2024-01-01 00:00:00+08:00 对应的 UTC 时刻，
# 换台 UTC 的机器跑，同一个 datetime 算出来的时间戳就不一样 —— 所以别对 naive 调 timestamp()

# ==================== 十四、时区处理 ====================
# ⭐⭐ 常用 —— 经常用
#
# Java 对照：
#   ZoneId.of("Asia/Shanghai")                     <->  ZoneInfo("Asia/Shanghai")
#   ZoneOffset.ofHours(8)                          <->  timezone(timedelta(hours=8))
#   zonedDateTime.withZoneSameInstant(ZoneOffset.UTC) <->  dt.astimezone(timezone.utc)
#
# 两种时区对象：
#   timezone      —— 固定偏移量，如 UTC、UTC+08:00。简单，但处理不了夏令时
#   ZoneInfo      —— 3.9+ 标准库，支持 IANA 时区名（Asia/Shanghai），自动处理夏令时和历史规则
#
# 铁律：数据库存 UTC，接口传 ISO8601 带时区，只在展示给用户时才转成本地时区。

CST = timezone(timedelta(hours=8))           # 东八区，固定偏移
print(CST)
# 输出值: UTC+08:00
print(CST.utcoffset(None))
# 输出值: 8:00:00

beijing = datetime(2024, 3, 15, 20, 0, 0, tzinfo=CST)
print(beijing)
# 输出值: 2024-03-15 20:00:00+08:00

utc_time = beijing.astimezone(timezone.utc)  # 转换成 UTC，时刻不变
print(utc_time)
# 输出值: 2024-03-15 12:00:00+00:00
print(beijing == utc_time)
# 输出值: True
# 两个 aware 对象比较的是"绝对时刻"，不是字面数字 —— 20:00+08:00 就是 12:00+00:00
print(beijing.utcoffset())
# 输出值: 8:00:00

# 用 ISO 格式存库/传输时，时区信息也一起带上，接收方才能还原
print(beijing.isoformat())
# 输出值: 2024-03-15T20:00:00+08:00

# === zoneinfo（3.9+ 标准库，推荐）===
# 用 IANA 时区名的好处：夏令时自动处理，不用自己算偏移量
shanghai = ZoneInfo("Asia/Shanghai")
new_york = ZoneInfo("America/New_York")
print(shanghai)
# 输出值: Asia/Shanghai

sh_dt = datetime(2024, 3, 15, 20, 0, 0, tzinfo=shanghai)
print(sh_dt)
# 输出值: 2024-03-15 20:00:00+08:00
print(sh_dt.utcoffset())
# 输出值: 8:00:00
print(sh_dt.astimezone(new_york))
# 输出值: 2024-03-15 08:00:00-04:00
# 3 月 15 日美国已进入夏令时，纽约是 UTC-4，所以是 08:00

summer_sh = datetime(2024, 6, 15, 20, 0, 0, tzinfo=shanghai)
winter_sh = datetime(2024, 12, 15, 20, 0, 0, tzinfo=shanghai)
print(summer_sh.astimezone(new_york))
# 输出值: 2024-06-15 08:00:00-04:00
print(winter_sh.astimezone(new_york))
# 输出值: 2024-12-15 07:00:00-05:00
# 同一个"北京 20 点"，夏天纽约是早上 8 点，冬天是早上 7 点 —— 夏令时是时区库自动处理的
# 用 timezone(timedelta(hours=-5)) 这种固定偏移写法，就永远算不对夏令时

# 常见时区名：UTC / Asia/Shanghai / America/New_York / Europe/London / Asia/Tokyo
# 完整列表：https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

# ==================== 十五、日期比较与区间判断 ====================
# ⭐⭐ 常用 —— 经常用
#
# datetime 对象重写了比较运算符，直接 < > == 就行，不用 Java 的 compareTo / isBefore / isAfter。
# 注意：比较只能用同类型且时区状态一致的对象（见第十六节的坑）。

d1 = date(2024, 3, 15)
d2 = date(2024, 3, 20)
print(d1 < d2)
# 输出值: True
print(d1 == date(2024, 3, 15))
# 输出值: True
print(d1 != d2)
# 输出值: True

# 区间判断：Python 支持链式比较，Java 必须写 a.compareTo(x) <= 0 && x.compareTo(b) <= 0
range_start = date(2024, 3, 1)
range_end = date(2024, 3, 31)
target = date(2024, 3, 15)
print(range_start <= target <= range_end)
# 输出值: True
print(range_start <= date(2024, 4, 1) <= range_end)
# 输出值: False

# 相差天数：日期相减得到 timedelta，取 .days
print((d2 - d1).days)
# 输出值: 5
print((range_end - range_start).days)
# 输出值: 30

# 排序：可直接 sort，因为实现了 __lt__
dates = [date(2024, 3, 20), date(2024, 1, 5), date(2024, 3, 1)]
print(sorted(dates))
# 输出值: [datetime.date(2024, 1, 5), datetime.date(2024, 3, 1), datetime.date(2024, 3, 20)]
# ⚠️ 列表打印用的是元素的 repr，所以长这样；想好看点自己转字符串
print([str(x) for x in sorted(dates)])
# 输出值: ['2024-01-05', '2024-03-01', '2024-03-20']

# 时间戳排序天然有序，日志按时间排序就是这个原理
events = [datetime(2024, 3, 15, 18, 0), datetime(2024, 3, 15, 9, 0), datetime(2024, 3, 15, 12, 0)]
print([x.strftime("%H:%M") for x in sorted(events)])
# 输出值: ['09:00', '12:00', '18:00']

# ==================== 十六、常见坑 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档

# --- 坑1：datetime 不可变，replace 返回新对象 ---
origin = datetime(2024, 3, 15, 14, 30, 0)
origin.replace(year=2025)          # 返回值被丢掉了，什么都不会发生
print("丢弃返回值后:", origin)
# 输出值: 丢弃返回值后: 2024-03-15 14:30:00
changed = origin.replace(year=2025)
print("接收返回值后:", changed)
# 输出值: 接收返回值后: 2025-03-15 14:30:00
# Java 的 java.time 也是这个行为；习惯了 java.util.Date 的 setYear 的人最容易踩

# --- 坑2：%Y 和 %y 的区别 ---
print(origin.strftime("%Y"))
# 输出值: 2024
print(origin.strftime("%y"))
# 输出值: 24
# Java 里 yyyy 是 4 位年、yy 是 2 位年；Python 用大小写区分，写错就少两位，肉眼很难发现

# --- 坑3：naive 和 aware 混用直接抛 TypeError ---
naive_dt = datetime(2024, 3, 15, 12, 0, 0)
aware_dt = datetime(2024, 3, 15, 12, 0, 0, tzinfo=timezone.utc)

try:
    naive_dt - aware_dt
except TypeError as exc:
    print("相减报错:", exc)
# 输出值: 相减报错: can't subtract offset-naive and offset-aware datetimes

try:
    naive_dt < aware_dt
except TypeError as exc:
    print("比较报错:", exc)
# 输出值: 比较报错: can't compare offset-naive and offset-aware datetimes
# Java 里 LocalDateTime 和 ZonedDateTime 类型不同编译期就报错了，
# Python 是动态类型，只能运行时才炸 —— 所以更要靠规范和类型提示约束自己：
# 项目里规定"所有 datetime 必须是 aware"，就能从源头避免

# --- 坑4：跨月/跨年用 timedelta 是安全的，按月加才危险 ---
print(datetime(2024, 12, 31, 23, 59, 59) + timedelta(seconds=1))
# 输出值: 2025-01-01 00:00:00
# 秒/分/时/天/周都是固定长度，跨年跨闰年都绝对安全

print(datetime(2024, 2, 29) + timedelta(days=365))
# 输出值: 2025-02-28 00:00:00
# 闰年 2 月 29 日加 365 天到 2025 年，落到了 2 月 28 日（2025 不是闰年，没有 2 月 29 日）

print(datetime(2024, 3, 31) + timedelta(days=30))
# 输出值: 2024-04-30 00:00:00
# 3 月 31 日"加一个月"得到 4 月 30 日 —— 天数对不上，账单日、到期日这类业务绝不能这么算，
# 必须用第十二节的 add_months() 或 dateutil.relativedelta

# --- 坑5：别拿字符串当日期比较 ---
print("2024-03-05" < "2024-03-15")
# 输出值: True
# ISO 格式的字符串恰好可以按字典序比较，但这是巧合，一旦格式变成 "2024/3/5" 就彻底错乱。
# 正确做法：先 strptime 转成 datetime 再比。
try:
    "2024/3/5" > datetime(2024, 3, 1)
except TypeError as exc:
    print("字符串和日期比大小:", exc)
# 输出值: 字符串和日期比大小: '>' not supported between instances of 'str' and 'datetime.datetime'
# 字符串和日期对象之间没有任何隐式转换，混着比直接 TypeError

# ==================== 清理演示产生的文件 ====================
# 关闭所有 handler（释放文件句柄），再删除日志目录。
# 真实项目不会删日志，这里是为了保持演示目录干净。
close_all_handlers()
shutil.rmtree(LOG_DIR, ignore_errors=True)
print("日志目录已清理:", not LOG_DIR.exists())
# 输出值: 日志目录已清理: True

print("=== 20 日志与日期时间 结束 ===")
