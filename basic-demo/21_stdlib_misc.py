"""
===== 第21课：常用标准库 =====
对标 Java 的 Jackson / commons-csv / picocli / UUID / MessageDigest
"""

import argparse
import base64
import contextlib
import csv
import glob
import hashlib
import hmac
import io
import json
import math
import os
import random
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path

# 本课所有文件类演示统一放在这个临时目录，结尾会整体删除
DEMO_DIR = Path("demo_21_tmp")
shutil.rmtree(DEMO_DIR, ignore_errors=True)
DEMO_DIR.mkdir(parents=True, exist_ok=True)

# ==================== 一、json（进阶）====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: Jackson 的 ObjectMapper / Gson（第9课只讲了最基础的 dump/load）

data = {"name": "张三", "age": 30, "city": "北京"}

# --- ensure_ascii=False：中文不转成 \uXXXX ---
# Java: objectMapper.writeValueAsString(obj) 默认就不转义，Python 默认转义，必须显式关闭
print(json.dumps(data))
# {"name": "\u5f20\u4e09", "age": 30, "city": "\u5317\u4eac"}（中文被转义成 \uXXXX，体积更大）
print(json.dumps(data, ensure_ascii=False))
# {"name": "张三", "age": 30, "city": "北京"}

# --- indent：美化输出（≈ Jackson 的 DefaultPrettyPrinter）---
print(json.dumps(data, ensure_ascii=False, indent=2))
# {
#   "name": "张三",
#   "age": 30,
#   "city": "北京"
# }

# --- sort_keys：按 key 排序，便于 diff / 做签名 ---
# Java: objectMapper.configure(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS, true)
print(json.dumps({"b": 1, "a": 2}, sort_keys=True))
# {"a": 2, "b": 1}

# --- separators：去掉多余空格，压缩体积（传输/落库场景）---
# 默认是 (', ', ': ')，indent 模式下默认变成 (',', ': ')
print(json.dumps({"a": 1, "b": [1, 2]}, separators=(",", ":")))
# {"a":1,"b":[1,2]}

# --- 反序列化参数 ---
# 严格模式：JSON 里出现 NaN/Infinity 会抛错（Java Jackson 默认也拒绝）
print(json.loads('{"a": 1}'))                 # {'a': 1}
print(json.loads('{"a": 1}', parse_int=float))  # {'a': 1.0}

# --- 默认不支持的类型：datetime / Decimal / set / 自定义对象 全部抛 TypeError ---
# Java: Jackson 有 JSR-310 模块自动支持 LocalDateTime，Python 标准库没有，必须自己处理
for bad in [datetime(2026, 9, 20, 10, 30, 0), Decimal("9.9"), {1, 2}, object()]:
    try:
        json.dumps({"v": bad})
    except TypeError as e:
        print(f"TypeError: {e}")
# TypeError: Object of type datetime is not JSON serializable
# TypeError: Object of type Decimal is not JSON serializable
# TypeError: Object of type set is not JSON serializable
# TypeError: Object of type object is not JSON serializable

# --- default=：自定义序列化函数（≈ Jackson 的 @JsonSerialize + 自定义 Serializer）---
# Java: public class MySerializer extends JsonSerializer<LocalDateTime> { ... }


def json_default(obj):
    """把 json 不认识的对象转成可序列化类型，转换不了就抛 TypeError 交给上层"""
    if isinstance(obj, (datetime, date)):
        # Java: @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(obj, Decimal):
        return float(obj)          # 金额场景建议 str(obj) 保精度
    if isinstance(obj, set):
        return sorted(obj, key=str)  # set 无序，排序后输出保证结果稳定
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(f"无法序列化的类型: {type(obj).__name__}")


payload = {
    "orderId": "ORD-001",
    "amount": Decimal("19.90"),
    "createdAt": datetime(2026, 9, 20, 10, 30, 0),
    "tags": {"vip", "new"},
    "file": Path("demo_21_tmp/users.csv"),
}
print(json.dumps(payload, ensure_ascii=False, default=json_default, sort_keys=True))
# {"amount": 19.9, "createdAt": "2026-09-20 10:30:00", "file": "demo_21_tmp/users.csv", "orderId": "ORD-001", "tags": ["new", "vip"]}

# --- object_hook：反序列化时把 dict 直接转成对象（≈ Jackson 的 @JsonCreator）---
# Java: objectMapper.readValue(json, Order.class)
class Order:
    """订单对象，演示 object_hook 反序列化"""

    def __init__(self, order_id, amount, created_at):
        self.order_id = order_id
        self.amount = amount
        self.created_at = created_at

    @classmethod
    def from_dict(cls, d):
        """把 json 解析出来的 dict 转成 Order 实例"""
        return cls(
            order_id=d.get("orderId"),
            amount=d.get("amount"),
            created_at=datetime.strptime(d["createdAt"], "%Y-%m-%d %H:%M:%S")
            if d.get("createdAt") else None,
        )

    def __repr__(self):
        return f"Order(order_id={self.order_id!r}, amount={self.amount!r}, created_at={self.created_at!r})"


raw_json = json.dumps(payload, ensure_ascii=False, default=json_default, sort_keys=True)
order = json.loads(raw_json, object_hook=Order.from_dict)
print(order.order_id)                          # ORD-001
print(order.amount)                            # 19.9（float，金额建议用 Decimal 二次转换）
print(order.created_at)                        # 2026-09-20 10:30:00
print(type(order).__name__)                    # Order

# ⚠️ object_hook 会对每一层 dict 都调用，嵌套结构要注意加类型判断，否则会误伤子 dict

# --- 落盘再读回：完整链路 ---
json_file = DEMO_DIR / "order.json"
with open(json_file, "w", encoding="utf-8") as f:
    # Java: objectMapper.writerWithDefaultPrettyPrinter().writeValue(file, obj)
    json.dump(payload, f, ensure_ascii=False, indent=2, default=json_default, sort_keys=True)

with open(json_file, "r", encoding="utf-8") as f:
    back = json.load(f, object_hook=Order.from_dict)
print(back)   # Order(order_id='ORD-001', amount=19.9, created_at=datetime.datetime(2026, 9, 20, 10, 30))

# ==================== 二、csv ====================
# ⭐⭐ 常用 —— 经常用，导出报表 / 批量导入必用
# Java: JDK 没有内置 CSV，必须引 OpenCSV 或 commons-csv；Python 标准库自带 csv
# 铁律：不要自己 line.split(",")！引号、逗号、换行的转义规则由 csv 模块处理

csv_file = DEMO_DIR / "users.csv"

# --- 写入：csv.writer ---
rows = [
    ["id", "name", "remark"],
    [1, "Alice", "普通用户"],
    [2, "Bob", '含逗号,和"引号"'],
    [3, "Carol", "含\n换行"],
]
# ⚠️ newline="" 必须加：否则 Windows 下每行之间会多一个空行
# Java: new CSVWriter(new OutputStreamWriter(new FileOutputStream(f), StandardCharsets.UTF_8))
with open(csv_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(rows[0])          # 单行写
    writer.writerows(rows[1:])        # 批量写

print(csv_file.read_text(encoding="utf-8"))
# （末尾会多一个空行，是 print 输出文件结尾换行符造成的）
# id,name,remark
# 1,Alice,普通用户
# 2,Bob,"含逗号,和""引号"""
# 3,Carol,"含
# 换行"

# --- 读取：csv.reader（自动还原转义）---
with open(csv_file, "r", encoding="utf-8", newline="") as f:
    reader = csv.reader(f)
    header = next(reader)             # 取表头
    print(header)                     # ['id', 'name', 'remark']
    for row in reader:
        print(f"{row[0]} -> {row[1]}")
# 1 -> Alice
# 2 -> Bob
# 3 -> Carol

# 引号里的逗号没有把我们骗到（自己 split 就会错）
with open(csv_file, "r", encoding="utf-8", newline="") as f:
    all_rows = list(csv.reader(f))
print(all_rows[2][2])                 # 含逗号,和"引号"
print(repr(all_rows[3][2]))           # '含\n换行'

# --- DictReader / DictWriter：按列名读写（≈ MyBatis 结果集映射成 Map）---
# Java: commons-csv 的 CSVRecord.get("name") / OpenCSV 的 BeanToCsv
with open(csv_file, "r", encoding="utf-8", newline="") as f:
    for record in csv.DictReader(f):
        print(record)
# {'id': '1', 'name': 'Alice', 'remark': '普通用户'}
# {'id': '2', 'name': 'Bob', 'remark': '含逗号,和"引号"'}
# {'id': '3', 'name': 'Carol', 'remark': '含\n换行'}

dict_csv = DEMO_DIR / "scores.csv"
fieldnames = ["name", "score"]
with open(dict_csv, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()                       # 写表头
    writer.writerow({"name": "Alice", "score": 90})
    writer.writerow({"name": "Bob", "score": 85})
    # 多余字段会抛 ValueError，缺字段填 restval（默认空字符串）
    writer.writerow({"name": "Carol", "score": 95})

with open(dict_csv, "r", encoding="utf-8", newline="") as f:
    print(list(csv.DictReader(f)))
# [{'name': 'Alice', 'score': '90'}, {'name': 'Bob', 'score': '85'}, {'name': 'Carol', 'score': '95'}]

# --- 编码坑：Windows 的 Excel 只认带 BOM 的 utf-8-sig，否则中文乱码 ---
excel_csv = DEMO_DIR / "excel.csv"
with open(excel_csv, "w", encoding="utf-8-sig", newline="") as f:
    csv.writer(f).writerow(["姓名", "城市"])

# 用普通 utf-8 读，表头第一个字段会多出一个 BOM 字符
with open(excel_csv, "r", encoding="utf-8", newline="") as f:
    print(repr(next(csv.reader(f))[0]))        # '﻿姓名'
# 用 utf-8-sig 读就正常
with open(excel_csv, "r", encoding="utf-8-sig", newline="") as f:
    print(next(csv.reader(f)))                 # ['姓名', '城市']

# ==================== 三、pathlib 补充 ====================
# ⭐⭐ 常用 —— 第9课讲了基础属性和 / 拼接，这里补充高频操作
# Java: java.nio.file.Files / Paths / Path

(DEMO_DIR / "sub" / "deep").mkdir(parents=True, exist_ok=True)
(DEMO_DIR / "a.txt").write_text("AAA", encoding="utf-8")
(DEMO_DIR / "b.log").write_text("BBB", encoding="utf-8")
(DEMO_DIR / "sub" / "c.txt").write_text("CCC", encoding="utf-8")
(DEMO_DIR / "sub" / "deep" / "d.txt").write_text("DDD", encoding="utf-8")
(DEMO_DIR / "demo.bin").write_bytes(b"\x00\x01\x02")

# --- 一行读写：read_text / write_text / read_bytes ---
# Java: Files.readString(path) / Files.writeString(path, content)（JDK11+）
print((DEMO_DIR / "a.txt").read_text(encoding="utf-8"))       # AAA
print((DEMO_DIR / "demo.bin").read_bytes())                   # b'\x00\x01\x02'
# 新增一行（append 语义等价于 Files.writeString(..., APPEND)）
with open(DEMO_DIR / "a.txt", "a", encoding="utf-8") as f:
    f.write("+tail")
print((DEMO_DIR / "a.txt").read_text(encoding="utf-8"))       # AAA+tail

# --- glob / rglob：通配查找 ---
# Java: Files.newDirectoryStream(dir, "*.txt")
print(sorted(p.name for p in DEMO_DIR.glob("*.txt")))
# ['a.txt']
print(sorted(p.name for p in DEMO_DIR.rglob("*.txt")))        # r = recursive
# ['a.txt', 'c.txt', 'd.txt']
print(sorted(p.name for p in DEMO_DIR.rglob("*.bin")))        # ['demo.bin']

# --- stat()：文件元信息 ---
# Java: Files.size(path) / Files.getLastModifiedTime(path)
st = (DEMO_DIR / "a.txt").stat()
print(st.st_size)                                             # 8（AAA+tail 共 8 字节）
print(type(st.st_mtime).__name__)                             # float
print((DEMO_DIR / "a.txt").stat().st_size > 0)                # True

# ==================== 四、glob 模块 ====================
# ⭐⭐ 常用 —— 处理历史遗留的字符串路径代码时经常见到
# Java: FileSystem.getPathMatcher("glob:**/*.txt")

old_cwd = os.getcwd()
os.chdir(DEMO_DIR)                 # 换成相对路径演示（glob 对相对/绝对都支持）

# --- glob.glob 返回 list，iglob 返回迭代器（惰性，大目录省内存）---
print(sorted(glob.glob("*.txt")))                 # ['a.txt']
print(sorted(glob.glob("*.log")))                 # ['b.log']
print(type(glob.iglob("*.txt")).__name__)         # generator

# --- 通配符 ---
print(sorted(glob.glob("[ab].*")))                # ['a.txt', 'b.log']（[ab] 匹配单个字符 a 或 b）
print(sorted(glob.glob("?.txt")))                 # ['a.txt']（? 匹配任意单个字符）
print(sorted(glob.glob("*.tx?")))                 # ['a.txt']

# --- ** 递归：必须配 recursive=True，否则 ** 等同 * ---
print(sorted(glob.glob("**/*.txt")))              # ['a.txt']（没开 recursive，只当一层 * 用）
print(sorted(glob.glob("**/*.txt", recursive=True)))
# ['a.txt', 'sub/c.txt', 'sub/deep/d.txt']
print(sorted(glob.glob("sub/**/*.txt", recursive=True)))
# ['sub/c.txt', 'sub/deep/d.txt']

os.chdir(old_cwd)                  # 还原工作目录

# ==================== 五、tempfile ====================
# ⭐⭐ 常用 —— 测试、给外部命令喂文件、中间结果落盘必用
# Java: File.createTempFile("prefix", ".suffix") + file.deleteOnExit()（清理还得自己兜底）

# --- NamedTemporaryFile：有名字的临时文件，with 退出即自动删除 ---
# ⚠️ 为什么必须用 with：delete=True 的删除动作挂在 __exit__ 上，
#    不用 with 就得手动 close + os.unlink，一旦中间抛异常文件就永久残留
with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8") as tmp:
    tmp.write("临时内容")
    tmp.flush()                                 # 不 flush 的话别的进程/命令读不到内容
    print(Path(tmp.name).exists())              # True
    print(Path(tmp.name).read_text(encoding="utf-8"))   # 临时内容
print(Path(tmp.name).exists())                  # False（with 退出后已自动删除）

# --- TemporaryDirectory：临时目录，退出时递归删掉整个目录树 ---
with tempfile.TemporaryDirectory() as tmp_dir:
    work = Path(tmp_dir) / "job" / "input.txt"
    work.parent.mkdir(parents=True, exist_ok=True)
    work.write_text("1,2,3", encoding="utf-8")
    print(work.exists())                        # True
    print(Path(tmp_dir).name.startswith("tmp")) # True（目录名形如 tmpXXXXXXXX）
print(Path(tmp_dir).exists())                   # False

# 实际场景：生成临时文件交给外部命令处理，处理完自动清理，不污染业务目录
with tempfile.TemporaryDirectory() as tmp_dir:
    src = Path(tmp_dir) / "data.txt"
    src.write_text("hello tempfile\n", encoding="utf-8")
    result = subprocess.run(["wc", "-l", str(src)], capture_output=True, text=True, check=True)
    print(result.stdout.split()[0])             # 1

# ==================== 六、random ====================
# ⭐⭐ 常用 —— 造测试数据用得最多；⚠️ 安全场景（令牌/密码/验证码）禁止使用，见下方 secrets
# Java: java.util.Random / ThreadLocalRandom.current() / SecureRandom

# --- 基础函数 ---
random.seed(42)                        # 固定种子，保证下面的输出可复现
print(random.random())                 # 0.6394267984578837（[0.0, 1.0) 之间）
print(random.randint(1, 100))          # 4（闭区间，两端都能取到）
print(random.uniform(1, 10))           # 7.673954497838496（浮点区间）
print(random.choice(["石头", "剪刀", "布"]))   # 石头（从序列里随机取一个）

# --- sample 不重复抽样 / shuffle 原地打乱 ---
random.seed(42)
print(random.sample(range(1, 50), 6))  # [41, 8, 2, 18, 16, 15]（抽 6 个不重复，像抽奖号码）
# Java: Collections.shuffle(list) / Random.ints(1, 50).distinct().limit(6)
cards = [1, 2, 3, 4, 5]
random.seed(42)
random.shuffle(cards)                  # ⚠️ 原地修改，返回 None
print(cards)                           # [4, 2, 3, 5, 1]

# --- seed() 的作用：结果可复现（单元测试断言随机逻辑时必须固定种子）---
# Java: new Random(42) 或 @FixedSeed；不固定种子时输出见下方注释
random.seed(42)
print(random.random())                 # 0.6394267984578837（与上面第一次完全相同）
print(random.random())                 # 0.025010755222666936（种固定了，跑多少次都是这个值）
# 不设置种子（或用系统时间做种）时结果每次都变：
random.seed()                          # 无参 = 用系统熵重新播种
print(f"{random.random():.6f}")        # 输出示例（每次不同，形如 0.244446）

# --- 安全场景：必须换成 secrets（标准库，密码学安全随机源）---
# Java: SecureRandom.getInstanceStrong()
print(len(secrets.token_hex(16)))       # 32（生成 16 字节随机数的十六进制串，形如 'a1b2...'）
print(len(secrets.token_urlsafe(16)))   # 22
print(secrets.choice(["A", "B", "C"]) in ["A", "B", "C"])   # True

# ==================== 七、os 与 sys ====================
# ⭐⭐ 常用
# Java: System.getenv / System.getProperty / File / System.exit

# --- 环境变量 ---
# Java: System.getenv("HOME") / System.getenv().getOrDefault("X", "默认值")
print(os.getenv("PATH") is not None)                 # True（本机一定有 PATH）
print(os.getenv("NOT_EXIST_ENV_XYZ", "默认值"))       # 默认值（不存在时给默认值，不会抛错）
os.environ["DEMO_APP_ENV"] = "dev"                   # 只影响当前进程，不会写回系统
print(os.environ["DEMO_APP_ENV"])                    # dev
print(os.getenv("DEMO_APP_ENV"))                     # dev
os.environ.pop("DEMO_APP_ENV", None)                 # 清理，避免影响后续演示

# --- 工作目录与目录操作 ---
# Java: System.getProperty("user.dir") / new File("x").mkdirs() / File.list()
print(os.path.basename(os.getcwd()))                 # basic-demo（当前工作目录名）
os.chdir(DEMO_DIR)
print(os.path.basename(os.getcwd()))                 # demo_21_tmp
os.makedirs("logs/2026", exist_ok=True)              # ≈ Files.createDirectories，exist_ok 避免已存在报错
print(sorted(os.listdir(".")))
# ['a.txt', 'b.log', 'demo.bin', 'excel.csv', 'logs', 'order.json', 'scores.csv', 'sub', 'users.csv']

# --- os.walk：递归遍历目录树（≈ Files.walkFileTree）---
for root, dirs, files in os.walk("."):               # 自顶向下
    dirs.sort()                                      # 原地排序，保证输出顺序稳定
    level = root.count(os.sep)
    print(f"{'  ' * level}{os.path.basename(root) or root}/")
    for name in sorted(files):
        print(f"{'  ' * (level + 1)}{name}")
# ./
#   a.txt
#   b.log
#   demo.bin
#   excel.csv
#   order.json
#   scores.csv
#   users.csv
#   logs/
#    2026/
#   sub/
#     c.txt
#     deep/
#       d.txt

# os.walk 也能删空目录（自底向上遍历）
os.rmdir("logs/2026")
os.rmdir("logs")
os.chdir(old_cwd)

# --- os.path 常用函数 ---
# Java: Paths.get(a, b) / Files.exists / path.getFileName() / String 截取后缀
print(os.path.join("data", "2026", "report.csv"))    # data/2026/report.csv
print(os.path.exists("demo_21_tmp/a.txt"))           # True
print(os.path.isfile("demo_21_tmp/a.txt"))           # True
print(os.path.isdir("demo_21_tmp/sub"))              # True
print(os.path.basename("/usr/local/app/run.log"))    # run.log
print(os.path.dirname("/usr/local/app/run.log"))     # /usr/local/app
print(os.path.splitext("report.tar.gz"))             # ('report.tar', '.gz')

# --- sys：解释器相关 ---
# Java: System.exit(code) / System.getProperty("java.version")
print(len(sys.argv) >= 1)                            # True
print(os.path.basename(sys.argv[0]))                 # 21_stdlib_misc.py（≈ Java 的 args[0] 是类名）
print(len(sys.argv) - 1)                             # 0（本次运行没传额外参数）
print(f"{sys.version_info.major}.{sys.version_info.minor}")   # 3.13
print(sys.platform)                                  # darwin（linux / win32）
print(os.path.isdir(sys.path[0]) or sys.path[0] == "")        # True（sys.path[0] 是脚本所在目录）


def exit_demo():
    """sys.exit 演示：抛 SystemExit，被上层捕获后不会真的退出进程"""
    # Java: System.exit(0) 直接终止 JVM，后面的代码永远执行不到
    try:
        sys.exit(3)
    except SystemExit as e:
        return e.code


print(exit_demo())                                   # 3（sys.exit(0) 表示正常，非 0 表示异常）

# ==================== 八、argparse 命令行参数 ====================
# ⭐⭐ 常用 —— 写运维脚本 / 工具类必用
# Java: 只能手写解析 main(String[] args)，或引 picocli / args4j / Spring Shell
# Python: 标准库 argparse，自动生成 -h 帮助、类型转换、参数校验、错误提示

# ⚠️ 本演示用 parse_args([...]) 传入假参数列表，绝不调用无参的 parse_args()
#    否则会去解析真实命令行，吃掉本文件的运行参数甚至直接退出


def build_parser():
    """构造命令行解析器"""
    parser = argparse.ArgumentParser(
        prog="import_tool.py",
        description="CSV 导入工具示例",
    )
    # 位置参数（必填）：对标 args[0]
    parser.add_argument("input", help="输入文件路径")
    # 可选参数：-o 短选项 / --output 长选项
    parser.add_argument("-o", "--output", default="out.txt", help="输出文件（默认 out.txt）")
    # type：自动类型转换（不需要 Integer.parseInt）
    parser.add_argument("-n", "--count", type=int, default=1, help="重复次数")
    # action="store_true"：布尔开关，出现即 True（Java picocli 的 @Option）
    parser.add_argument("-v", "--verbose", action="store_true", help="打印详细日志")
    # choices：限定取值范围，非法值直接报错退出
    parser.add_argument("--level", choices=["debug", "info", "warn"], default="info", help="日志级别")
    # nargs="*"：接收 0 到 N 个值
    parser.add_argument("--tags", nargs="*", default=[], help="标签列表")
    # required=True：可选项也能设成必填
    parser.add_argument("--app-key", required=True, help="应用密钥（必填）")
    return parser


def demo_argparse():
    """演示参数解析（全部使用假参数列表，不影响真实命令行）"""
    parser = build_parser()

    # 自动生成的用法说明
    print(parser.format_usage().strip())
    # usage: import_tool.py [-h] [-o OUTPUT] [-n COUNT] [-v]
    #                       [--level {debug,info,warn}] [--tags [TAGS ...]]
    #                       --app-key APP_KEY
    #                       input

    args = parser.parse_args(
        ["data.csv", "-n", "3", "-v", "--level", "debug", "--tags", "a", "b", "--app-key", "K1"]
    )
    print(args.input)                  # data.csv
    print(args.output)                 # out.txt（没传就用 default）
    print(args.count)                  # 3（已经是 int，不用转换）
    print(args.verbose)                # True
    print(args.level)                  # debug
    print(args.tags)                   # ['a', 'b']
    print(vars(args))
    # {'input': 'data.csv', 'output': 'out.txt', 'count': 3, 'verbose': True, 'level': 'debug', 'tags': ['a', 'b'], 'app_key': 'K1'}
    # 短选项等价写法
    print(parser.parse_args(["d.csv", "-n", "5", "--app-key", "K2"]).count)   # 5

    # 缺必填参数 / 传非法 choices 时，argparse 会打印错误并抛 SystemExit(2)
    # 这里把 stderr 重定向掉，避免污染演示输出
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        try:
            parser.parse_args([])                      # 缺 input 和 --app-key
        except SystemExit as e:
            print(f"参数不合法 -> SystemExit 退出码 = {e.code}")   # 2
    print(buf.getvalue().strip().splitlines()[-1])
    # import_tool.py: error: the following arguments are required: input, --app-key

    # 生产写法：真实脚本里就该这么用（本文件不执行下面这段）
    # if __name__ == "__main__":
    #     opts = build_parser().parse_args()      # 无参 = 解析真实命令行
    #     print(opts.input, opts.count)


if __name__ == "__main__":
    demo_argparse()

# ==================== 九、加密与编码 ====================
# ⭐⭐ 常用 —— 做接口签名、存密码、生成 ID 必用
# Java: MessageDigest / Base64 / java.util.UUID / javax.crypto.Mac

# --- hashlib：摘要（哈希）---
# Java: MessageDigest.getInstance("SHA-256").digest(bytes)
print(hashlib.md5(b"hello").hexdigest())
# 5d41402abc4b2a76b9719d911017c592
print(hashlib.sha256(b"hello").hexdigest())
# 2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
print(len(hashlib.sha256(b"hello").hexdigest()))       # 64（十六进制字符数 = 256/4）
print(hashlib.sha256("中文也能摘要".encode("utf-8")).hexdigest()[:16])   # 14e05ea719c9423f（结果固定，取前 16 位）

# ⚠️ md5 已被证明可碰撞，禁止用于签名/密码；密码存储用 bcrypt / argon2（第三方库）
#     pip install bcrypt  →  bcrypt.hashpw(pwd, bcrypt.gensalt())

# --- 加盐：同样的密码得到不同摘要，防彩虹表 ---
salt = "s@lt_2026"
print(hashlib.sha256(("hello" + salt).encode("utf-8")).hexdigest())
# fad0706b7d6a10417a4b628d18dfc7c3a3680c147ab1f901dc2fa45778dafb27
# Java: MessageDigest md = MessageDigest.getInstance("SHA-256"); md.update((pwd + salt).getBytes())
# 更规范的做法：每个用户一个随机 salt，和摘要一起存库
user_salt = secrets.token_hex(8)
user_hash = hashlib.sha256((user_salt + "hello").encode("utf-8")).hexdigest()
print(len(user_salt))                                  # 16
print(len(user_hash))                                  # 64

# --- base64：把二进制转成可安全放进 JSON / URL / 邮件的文本 ---
# Java: java.util.Base64.getEncoder().encodeToString(bytes)
token = base64.b64encode("你好，Python".encode("utf-8"))
print(token)                                           # b'5L2g5aW977yMUHl0aG9u'
print(token.decode("ascii"))                           # 5L2g5aW977yMUHl0aG9u
# 解码（≈ Base64.getDecoder().decode(s)）
print(base64.b64decode("5L2g5aW977yMUHl0aG9u").decode("utf-8"))   # 你好，Python
# ⚠️ base64 只是编码不是加密，任何人都能还原，不能用来保护敏感数据
# URL 安全变体：把 +/ 换成 -_，去掉结尾的 =（JWT 用这个）
print(base64.urlsafe_b64encode(b"\xfb\xff\xfe").decode("ascii"))   # -__-
print(len(base64.b64encode(b"\x00" * 32).decode("ascii")))         # 44（32 字节 → 44 字符）

# --- uuid ---
# Java: UUID.randomUUID().toString()
uid = uuid.uuid4()
print(uid)                                             # 输出示例（每次不同，形如 3f2504e0-4f89-41d3-9a0c-0305e82c3301）
print(len(str(uid)))                                   # 36（8-4-4-4-12 共 36 个字符）
print(uid.version)                                     # 4（随机生成）
print(str(uid).count("-"))                             # 4
uid5 = uuid.uuid5(uuid.NAMESPACE_DNS, "example.com")   # 由命名空间+名字推导，结果确定
print(uid5)                                            # cfbff0d1-9375-5685-968c-48ce8b15ae17（输入相同则结果永远相同）
print(uid5.version)                                    # 5

# --- hmac：带密钥的摘要，接口签名防篡改（比直接 sha256(参数+密钥) 更安全）---
# ⭐ 了解 —— 对接第三方支付/开放平台时才会用到
# Java: Mac mac = Mac.getInstance("HmacSHA256"); mac.init(new SecretKeySpec(key, "HmacSHA256"))
sign = hmac.new(b"secret-key", b"hello", hashlib.sha256).hexdigest()
print(sign)
# 98e7ffb964bb5a3f902db1fc101a5baa98b6f2cd56858210c9d70f26ac762fc7
print(hmac.compare_digest(sign, hmac.new(b"secret-key", b"hello", hashlib.sha256).hexdigest()))   # True
# ⚠️ 验签必须用 hmac.compare_digest（恒定时间比较），不要用 == ，防时序攻击

# ==================== 十、subprocess ====================
# ⭐ 了解 —— 调用外部命令 / 脚本时用
# Java: new ProcessBuilder("ls", "-l").start()
# Python 的 subprocess.run 是同步阻塞版，直接拿结果，比 Java 读流方便得多

# --- 基本用法：capture_output 抓输出，text=True 按字符串处理，check=True 非 0 退出码抛异常 ---
result = subprocess.run(
    ["echo", "hello from subprocess"],
    capture_output=True, text=True, check=True,
)
print(result.returncode)                 # 0
print(repr(result.stdout))               # 'hello from subprocess\n'
print(repr(result.stderr))               # ''

# 参数用 list 传，不要拼字符串
result = subprocess.run(["python3", "-c", "print(1 + 1)"], capture_output=True, text=True, check=True)
print(result.stdout.strip())             # 2

# 不想让 check=True 抛异常时，自己判断 returncode
result = subprocess.run(["ls", str(DEMO_DIR)], capture_output=True, text=True)
print(result.returncode)                 # 0
print("a.txt" in result.stdout)          # True

# --- ⚠️ 安全提醒：绝不要 shell=True + 拼接用户输入 ---
# 用户输入 "; rm -rf /" 会被 shell 当成命令执行（命令注入）
# 错误写法： subprocess.run(f"ls {user_input}", shell=True)
# 正确写法： subprocess.run(["ls", user_input])       ← 参数作为独立 argv 传递，不经过 shell
# shell=True 只在必须用管道/重定向时才考虑，且参数必须由程序内部固定

# ==================== 十一、其他小工具 ====================
# ⭐ 了解 —— 用到再查
# Java: System.currentTimeMillis() / System.nanoTime() / Math

# --- time ---
# Java: Thread.sleep(10) / System.currentTimeMillis() / System.nanoTime()
sleep_start = time.perf_counter()
time.sleep(0.01)                                    # 秒为单位，阻塞当前线程
sleep_cost = time.perf_counter() - sleep_start
print(sleep_cost >= 0.01)                           # True
print(f"{sleep_cost:.3f}")                          # 输出示例（每次不同，约 0.010）
print(len(str(int(time.time()))))                   # 10（秒级时间戳，10 位整数）
print(int(time.time()) > 1_700_000_000)             # True（Unix 时间戳，本地时区无关）
# perf_counter 用单调时钟，专门用来测耗时；time() 会受系统时间调整影响，别用来计时
print(time.perf_counter() > 0)                      # True（数值每次不同，从某个任意起点算起）
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(0)))   # 1970-01-01 08:00:00（东八区）

# --- math ---
# Java: Math.ceil / Math.floor / Math.sqrt / Math.abs
print(math.ceil(2.1))                               # 3（向上取整）
print(math.floor(2.9))                              # 2（向下取整）
print(math.sqrt(16))                                # 4.0（返回 float，不是 int）
print(math.factorial(5))                            # 120（5!）
print(math.gcd(12, 18))                             # 6（Java 是 BigInteger.gcd）
print(math.isclose(0.1 + 0.2, 0.3))                 # True（浮点误差专用比较，别用 ==）
print(0.1 + 0.2 == 0.3)                             # False（经典浮点坑）
print(round(0.1 + 0.2, 10) == 0.3)                  # True（或 round 到指定精度再比）
# 金额场景用 decimal.Decimal，不要用 float
print(Decimal("0.1") + Decimal("0.2"))              # 0.3（精确十进制运算）
print(math.isclose(1.0, 1.0000001))                 # False（默认相对容差 1e-9）

# ==================== 清理临时文件 ====================
shutil.rmtree(DEMO_DIR, ignore_errors=True)
print(DEMO_DIR.exists())                            # False

print("=== 21 常用标准库 结束 ===")
