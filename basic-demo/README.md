# Python 基础学习（Java 开发者视角）

面向**有 Java 基础**的开发者。每节课都是一个独立可运行的文件，注释里全程对照 Java 写法，
只讲"和 Java 不一样的地方"，不重复讲编程常识。

## 运行方式

```bash
# 在 basic-demo 目录下（使用项目自带 venv）
cd /Users/wanws/pythonCoding/python-learn-project/basic-demo
../.venv/bin/python 01_basics.py

# 01_basics.py 有 input()，需要喂输入
echo "测试" | ../.venv/bin/python 01_basics.py
```

## 常用度标记

每个知识点上方都有标记，用于区分"必须背下来"和"用到再查"：

| 标记 | 含义 | 判断标准 |
|---|---|---|
| ⭐⭐⭐ | **必会** | 天天写，不应该查文档 |
| ⭐⭐ | **常用** | 经常用，需要熟悉 |
| ⭐ | **了解** | 知道有这么回事，用的时候查文档 |

## 课程地图

### 第一阶段：语言基础

| 课 | 文件 | 内容 | 对标 Java |
|---|---|---|---|
| 01 | `01_basics.py` | 基础语法、缩进、`__main__` | 类包裹、main 方法 |
| 02 | `02_datatypes.py` | int/float/str/bool/None、Decimal | 8 种基本类型 + 包装类 |
| 03 | `03_strings.py` | 字符串、格式化、切片 | String / StringBuilder |
| 04 | `04_collections.py` | list / tuple / set / dict | ArrayList / HashSet / HashMap |
| 05 | `05_control_flow.py` | if / for / while / match-case | if / for / switch |
| 06 | `06_functions.py` | 函数、默认参数、可变参数、装饰器 | 方法重载、可变参数 |

### 第二阶段：OOP 与工程

| 课 | 文件 | 内容 | 对标 Java |
|---|---|---|---|
| 07 | `07_oop.py` | 类、继承、@property、ABC | class / extends / interface |
| 08 | `08_exceptions.py` | try-except-else-finally、raise、异常链 | try-catch-finally / throws |
| 09 | `09_file_io.py` | 文件读写、with、pathlib、json | FileInputStream / Files |
| 10 | `10_modules.py` | import、包、`__init__.py`、pip | import / package / Maven |

### 第三阶段：语言特性进阶

| 课 | 文件 | 内容 | 对标 Java |
|---|---|---|---|
| 11 | `11_advanced.py` | 推导式、生成器、装饰器、枚举、dataclass 总览 | —— |
| 12 | `12_operators.py` | 运算符、`//`、`**`、链式比较、海象 `:=` | 运算符（多处行为不同） |
| 13 | `13_syntax_sugar.py` | **语法糖大全**：解包、合并、推导式、f-string 进阶 | 大量样板代码 |
| 14 | `14_builtins.py` | 内置函数、`collections`、`itertools` | Collections 工具类 / Guava |
| 15 | `15_mutability_copy.py` | **可变性、引用与拷贝**（Java 开发者踩坑最多） | 引用传递 / clone |
| 16 | `16_oop_advanced.py` | `@classmethod` / `@staticmethod`、MRO、`__slots__`、魔法方法 | static / 多继承 |
| 17 | `17_scope_closure.py` | LEGB、闭包、`functools`、装饰器进阶 | AOP 注解 |
| 18 | `18_typing_advanced.py` | 类型提示、`Protocol`、`TypeVar`、dataclass 进阶 | 泛型 / 注解 |

### 第四阶段：标准库与并发

| 课 | 文件 | 内容 | 对标 Java |
|---|---|---|---|
| 19 | `19_regex.py` | `re` 正则全部常用 API + 实战 | Pattern / Matcher |
| 20 | `20_logging_datetime.py` | `logging` + `datetime` | slf4j/logback + java.time |
| 21 | `21_stdlib_misc.py` | json / csv / glob / tempfile / random / argparse / hashlib | Jackson / picocli / MessageDigest |
| 22 | `22_concurrency_async.py` | GIL、锁、线程池、`asyncio` | Thread / ExecutorService / 虚拟线程 |

## ⭐⭐⭐ 必会速查（最高频写法）

### 基础
```python
name = "Alice"                    # 无类型声明
if x is None:                     # 判空用 is，不用 ==
f"{name} 今年 {age} 岁"           # f-string，永远优先用它
f"{pi:.2f}"                       # 保留两位小数
print(a, b, sep=", ", end="")     # 分隔符与结尾
```

### 容器
```python
lst.append(x)                     # 追加
d.get(key, "默认值")              # 安全取值
for k, v in d.items():            # 遍历字典
if not lst:                       # 空集合判断
lst[1:3]  /  lst[::-1]            # 切片 / 反转
[x * 2 for x in nums if x > 0]    # 列表推导式
{w: len(w) for w in words}        # 字典推导式
```

### 控制流
```python
for i, v in enumerate(lst):       # 带索引遍历
for a, b in zip(list1, list2):    # 并行遍历
"成年" if age >= 18 else "未成年"  # 三元表达式
0 <= score <= 100                 # 链式比较
match status: case 200: ...       # 模式匹配
```

### 函数
```python
def f(a, b=1, *args, **kwargs):   # 默认参数 / 可变参数
name, age = get_user()            # 多返回值解包
sorted(data, key=lambda x: x.age) # lambda 排序
@decorator                        # 装饰器
```

### OOP
```python
class Dog:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return f"Dog({self.name})"

class Puppy(Dog):                 # 继承
    def __init__(self, name, toy):
        super().__init__(name)
```

### 异常与 IO
```python
try:
    ...
except ValueError as e:
    ...
finally:
    ...

with open("f.txt", "r", encoding="utf-8") as f:   # 自动关闭
    content = f.read()

json.dump(data, f, ensure_ascii=False, indent=2)
```

### 惯用法（Java 没有）
```python
a, b = b, a                       # 交换
first, *rest = [1, 2, 3]          # 星号解包
{**d1, **d2}  /  d1 | d2          # 合并字典
[*a, *b]                          # 合并列表
value = user_input or "默认值"     # 短路兜底
while (line := f.readline()):     # 海象运算符
if __name__ == "__main__":        # 入口保护
```

## ⚠️ 关于输出里的 Error / Exception 字样

有 8 节课会**故意触发异常**来讲解异常类型和行为。这些异常全部被 `try/except` 捕获，
**脚本正常退出，不是报错**。这些文件的开头都会打印一行预告：

```
⚠️ 本课会故意触发若干异常用于教学演示，它们都会被 try/except 捕获，
   控制台出现 Error / Exception 字样属正常现象，脚本退出码为 0
```

| 课 | 会看到什么 |
|---|---|
| 08 | 各类内置异常（ValueError / AttributeError …） |
| 15 | 引用与拷贝相关的错误、循环引用 |
| 16 | `__slots__` 属性限制、不可哈希对象作 dict key |
| 17 | 作用域 `NameError` / `UnboundLocalError`、闭包陷阱 |
| 18 | 类型检查失败、frozen dataclass 赋值失败、`__post_init__` 校验 |
| 19 | 匹配失败返回 `None` 后调用 `.group()` 的 AttributeError |
| 20 | `logger.exception()` 会打印**两段完整 Traceback**（最像崩溃，实为教学演示） |
| 22 | `asyncio.gather(return_exceptions=True)` 的异常收集 |

**判断脚本是否真的正常，看退出码，不要看输出：**

```bash
../.venv/bin/python 20_logging_datetime.py; echo "退出码=$?"
# 退出码=0  → 一切正常
```

## 高频踩坑清单

| 坑 | 说明 |
|---|---|
| `/` 永远返回 float | 整数除法用 `//` |
| 没有 `++` / `--` | 写 `i += 1` |
| 负数整除/取模与 Java 不同 | `-7 // 2 == -4`，`-7 % 3 == 2` |
| `and` / `or` 返回操作数 | 不是布尔，需要布尔就套 `bool()` |
| 默认参数用可变对象 | `def f(lst=[])` 会被所有调用共享，用 `None` 兜底 |
| 连等赋值可变对象 | `a = b = []` 是两个名字指向同一个 list |
| 装饰器忘记 `functools.wraps` | 函数名变成 `wrapper` |
| 多进程不写 `__main__` 保护 | macOS/Windows 下进程无限自我复制 |
| `set` 不保证顺序 | 只有 `dict` 有插入序保证 |
| 类型提示运行时不检查 | 需要 mypy/pyright 才有意义 |
| 浅拷贝嵌套结构 | 改内层会影响原对象，用 `copy.deepcopy` |
| 在 asyncio 里调 `time.sleep` | 会阻塞整个事件循环 |
