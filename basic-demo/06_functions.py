"""
===== 第6课：函数 =====
对标 Java 的方法（method），但 Python 的函数更灵活
"""

# ==================== 定义函数 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: public int add(int a, int b) { return a + b; }
def add(a, b):           # def + 函数名 + 参数（无需类型）
    """两数相加"""        # 文档字符串（类似 Java 的 Javadoc，不强制）
    return a + b

print(add(3, 5))         # 8

# ==================== 类型注解（可选，仅提示）====================
# ⭐⭐ 常用 —— 经常用
# Java 强制类型，Python 可写可不写
def greet(name: str, age: int) -> str:
    return f"{name} 今年 {age} 岁"

print(greet("Tom", 25))

# 注解是提示，不强制：
print(greet(123, "abc"))  # 也能运行！（但 IDE 会警告）

# ==================== 默认参数（Java 不支持）====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java 重载才能实现：method(a), method(a, b)
def connect(host: str, port: int = 3306):
    print(f"连接 {host}:{port}")

connect("localhost")       # 使用默认端口 3306
connect("localhost", 5432) # 自定义端口

# ⭐⭐ 常用 —— 经常用
# ⚠️ 注意：默认参数只用一次，不要用可变对象
def bad_append(item, lst=[]):    # ❌ 默认 [] 被所有调用共享
    lst.append(item)
    return lst

print(bad_append(1))       # [1]
print(bad_append(2))       # [1, 2] ← 不是 [2]！

def good_append(item, lst=None):  # ✅ 用 None 代替
    if lst is None:
        lst = []
    lst.append(item)
    return lst

# ==================== 可变参数 ====================
# ⭐⭐ 常用 —— 经常用
# Java: public void printAll(String... args) { ... }
def print_all(*args):          # * 号 = 任意数量参数 → 元组
    for arg in args:
        print(arg, end=" ")
    print()

print_all("a", "b", "c")       # a b c

# 关键字参数
# ⭐⭐ 常用 —— 经常用
# Java：无直接对应，通常用 @Builder 或重载
def create_user(**kwargs):     # ** 号 = 任意关键字参数 → 字典
    print(kwargs)

create_user(name="Bob", age=30, city="Beijing")

# ==================== 返回值 ====================
# ⭐⭐ 常用 —— 经常用
# Java：只能返回一个对象（用类或 Record 包装）
# Python 可返回多个值（本质是元组）
def get_user():
    return "Alice", 25, "alice@example.com"

name, age, email = get_user()  # 解包
print(name, age, email)

# ==================== lambda 表达式（对标 Java 8 Lambda）====================
# ⭐⭐ 常用 —— 经常用
# Java: (a, b) -> a + b
add_lambda = lambda a, b: a + b
print(add_lambda(3, 5))        # 8

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# lambda 常用于排序
pairs = [(1, "one"), (3, "three"), (2, "two")]
pairs.sort(key=lambda x: x[0]) # 按第一个元素排序
print(pairs)

# ⭐ 了解 —— 用到再查
# Java Stream 操作在 Python 中用推导式/函数式：
nums = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, nums))
filtered = list(filter(lambda x: x > 2, nums))
from functools import reduce
summed = reduce(lambda a, b: a + b, nums)
print(doubled, filtered, summed)

# ==================== 函数是一等公民 ====================
# ⭐⭐ 常用 —— 经常用
def apply(func, value):
    return func(value)

result = apply(lambda x: x * 2, 10)
print(result)                  # 20

# ⭐⭐ 常用 —— 经常用
# 函数可以嵌套
def outer(text: str):
    def inner():              # 类似 Java 的内部方法
        print(f"内部函数: {text}")
    inner()

outer("你好")

# ==================== 装饰器（Python 独有，Java 用 AOP 注解）====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
import functools

def log_calls(func):
    # ⚠️ 必须加 @functools.wraps，否则 hello.__name__ 会变成 "wrapper"、__doc__ 丢失
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"调用: {func.__name__}({args}, {kwargs})")
        return func(*args, **kwargs)
    return wrapper

@log_calls             # 相当于 hello = log_calls(hello)
def hello(name):
    return f"Hello, {name}"

print(hello("World"))

print("=== 06 函数 结束 ===")
