"""
===== 第11课：高级特性总览 =====
Java 没有、但对 Java 开发者很实用的 Python 独有特性
本课是"地图"：每个特性只给最小可运行示例，深入内容见对应的后续课程

⚠️ 结构说明：本文件所有逻辑都放在 main() 里、由 if __name__ == "__main__" 调用。
   原因见 demo_concurrency()——创建进程池的代码如果写在模块顶层，
   macOS / Windows 用 spawn 启动子进程时会重新 import 本模块，导致顶层代码重复执行甚至无限递归。
   这不是本文件为了好看才这么写，而是 Python 多进程项目必须遵守的硬性约束。
"""

import time
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from contextlib import contextmanager


# ==================== 一、推导式（⭐⭐⭐ 必会）→ 详见第13课 ====================
def demo_comprehension():
    # Java: list.stream().filter(x -> x % 2 == 0).map(x -> x * 2).collect(toList())
    nums = [1, 2, 3, 4, 5, 6]
    result = [x * 2 for x in nums if x % 2 == 0]
    print(result)                  # [4, 8, 12]

    # 嵌套推导式：展平二维列表
    # Java: matrix.stream().flatMap(List::stream).collect(toList())
    matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    flattened = [num for row in matrix for num in row]
    print(flattened)               # [1, 2, 3, 4, 5, 6, 7, 8, 9]

    # 字典推导式
    # Java: Collectors.toMap
    squares = {x: x ** 2 for x in range(5)}
    print(squares)                 # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}


# ==================== 二、生成器（⭐⭐⭐ 必会）====================
# Java 没有对应语法（Stream 是惰性的，但写法是链式 API，不是语言级 yield）
def count_up_to(n):
    """生成器函数：yield 像 return，但会保留现场，下次从这里继续"""
    i = 1
    while i <= n:
        yield i                    # 产出值并挂起，函数状态不丢失
        i += 1


def demo_generator():
    for num in count_up_to(5):
        print(num, end=" ")        # 1 2 3 4 5
    print()

    # 生成器表达式（圆括号）：惰性求值，百万级数据几乎不占内存
    squares_gen = (x * x for x in range(1000000))
    print(next(squares_gen))       # 0
    print(next(squares_gen))       # 1

    # 💡 选型：数据量大且只遍历一次 → 生成器；需要 len/索引/反复遍历 → 列表
    print(sum(x for x in range(1000) if x % 3 == 0))   # 166833（sum 内部逐个消费，不建中间列表）


# ==================== 三、装饰器（⭐⭐⭐ 必会）→ 详见第17课 ====================
# 对标 Java 的 @Transactional / @Cacheable 等 AOP 注解，但 Python 装饰器是语言级语法，不需要容器
import functools


def timer(func):
    """测量函数执行时间（≈ Spring 的 @Around 环绕通知）"""
    @functools.wraps(func)         # ⚠️ 必须加，否则 func.__name__ 会变成 wrapper
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        cost = time.perf_counter() - start
        print(f"{func.__name__} 耗时: {cost:.4f}s")
        return result
    return wrapper


@timer                             # 等价于 slow_function = timer(slow_function)
def slow_function():
    time.sleep(0.1)
    return "done"


def demo_decorator():
    result = slow_function()       # 输出示例：slow_function 耗时: 0.1003s
    print(result)                  # done
    print(slow_function.__name__)  # slow_function（靠 functools.wraps 保住的名字）


# ==================== 四、上下文管理器（⭐⭐⭐ 必会）→ 详见第9、17课 ====================
# Java 的 try-with-resources 只支持 AutoCloseable，Python 的 with 可以用于任何对象
class Timer:
    """基于类的上下文管理器：__enter__ 进入时执行，__exit__ 退出时执行（异常也会执行）"""

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cost = time.perf_counter() - self.start
        print(f"耗时: {self.cost:.4f}s")
        return False               # 返回 False = 不吞异常，异常继续往外抛（返回 True 则吞掉）


@contextmanager
def simple_timer():
    """基于生成器的写法（更简洁）：yield 之前是 __enter__，之后是 __exit__"""
    start = time.perf_counter()
    yield                          # with 块的代码在这里执行
    print(f"耗时: {time.perf_counter() - start:.4f}s")


def demo_context_manager():
    with Timer():
        sum(range(1000000))        # 输出示例：耗时: 0.0139s

    with simple_timer():
        sum(range(1000000))        # 输出示例：耗时: 0.0136s

    # 💡 with 也能同时管理多个资源（第13课有示例），比 Java 的嵌套 try-with-resources 清爽


# ==================== 五、并发（⭐⭐⭐ 必会）→ 详见第22课 ====================
def worker(name: str):
    print(f"  线程 {name} 运行")


def square(n: int) -> int:
    return n * n


def demo_concurrency():
    # --- 多线程（≈ Java Thread）---
    # ⚠️ Python 有 GIL，多线程只对 IO 密集有效，CPU 密集必须用多进程
    threads = []
    for i in range(3):
        t = Thread(target=worker, args=(f"T{i}",))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()                   # Java: t.join()

    # --- 线程池（≈ Java ExecutorService）---
    # Java: ExecutorService pool = Executors.newFixedThreadPool(4);
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(worker, f"P{i}") for i in range(4)]
        for f in futures:
            f.result()             # 取结果，同时保证异常不被吞掉

    # --- 多进程（Java 没有内置，需要自己起进程或第三方库）---
    # CPU 密集型用 multiprocessing 绕过 GIL
    # ⚠️ 致命陷阱：这段代码如果写在模块顶层，macOS / Windows 的 spawn 模式会
    #    在子进程里重新执行一遍 → 又创建子进程 → 无限自我复制（进程爆炸，实测卡死）。
    #    必须放在 if __name__ == "__main__" 保护内。Linux 的 fork 模式可以侥幸不写，但别依赖。
    with Pool(4) as pool:
        result = pool.map(square, range(10))
        print(result)              # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]


# ==================== 六、枚举（⭐⭐⭐ 必会）====================
# Java: public enum Color { RED, GREEN, BLUE }
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


# 对标 Java 带字段和构造器的 enum
# Java: enum HttpStatus { OK(200, "成功"); private final int code; ... }
class HttpStatus(Enum):
    OK = (200, "成功")
    NOT_FOUND = (404, "未找到")
    SERVER_ERROR = (500, "服务器错误")

    def __init__(self, code: int, desc: str):
        self.code = code
        self.desc = desc

    @classmethod
    def from_code(cls, code: int) -> "HttpStatus":
        """按状态码反查枚举（Java 的 valueOf 只支持名字，按字段查要自己写）"""
        for status in cls:
            if status.code == code:
                return status
        raise ValueError(f"未知状态码: {code}")


def demo_enum():
    print(Color.RED)               # Color.RED（打印出来就是这个名字，Java 是 toString）
    print(Color.RED.name)          # RED
    print(Color.RED.value)         # 1
    print(Color.RED is Color.RED)  # True（枚举成员天生单例，用 is 比较即可）

    for c in Color:
        print(f"{c.name} = {c.value}")   # RED = 1 / GREEN = 2 / BLUE = 3

    print(HttpStatus.from_code(404).desc)   # 未找到

    # ⚠️ 枚举成员不能比较大小，也不能修改
    # print(Color.RED < Color.BLUE)   # ❌ TypeError


# ==================== 七、数据类（⭐⭐⭐ 必会）→ 详见第18课 ====================
# Java: record Point(int x, int y) {}
# 自动生成 __init__ / __repr__ / __eq__（不含 __hash__ 除非 frozen=True）
@dataclass
class Point:
    x: int
    y: int


@dataclass
class User:
    name: str
    age: int = 0
    # ⚠️ 可变默认值必须用 field(default_factory=...)，不能写 tags: list = []
    #    原因见第15课：默认值只在定义时创建一次，会被所有实例共享
    tags: list = field(default_factory=list)


def demo_dataclass():
    p1 = Point(1, 2)
    p2 = Point(1, 2)
    print(p1)                      # Point(x=1, y=2)
    print(p1 == p2)                # True（自动实现了 equals，Java 里得手写或上 Lombok）

    u1, u2 = User("Alice"), User("Bob")
    u1.tags.append("VIP")
    print(u1.tags)                 # ['VIP']
    print(u2.tags)                 # []（互不影响，因为 default_factory 每个实例各建一个）


# ==================== 八、类型提示（⭐⭐⭐ 必会）→ 详见第18课 ====================
# Java: public String greet(String name, int age) { ... }
def greet(name: str, age: int = 0) -> str:
    return f"{name} is {age}"


def demo_typing():
    print(greet("Tom", 25))        # Tom is 25
    # ⚠️ 类型提示运行时完全不检查，这里传错类型照样能跑
    print(greet(123, "abc"))       # 123 is abc（IDE 会警告，解释器不管）

    names: list[str] = ["Alice", "Bob"]          # 3.9+ 推荐用小写内置泛型
    scores: dict[str, int] = {"Alice": 90}
    maybe_name: Optional[str] = None             # 等价于 str | None
    print(names, scores, maybe_name)             # ['Alice', 'Bob'] {'Alice': 90} None


# ==================== 程序入口 ====================
def main():
    print("--- 1. 推导式 ---")
    demo_comprehension()
    print("--- 2. 生成器 ---")
    demo_generator()
    print("--- 3. 装饰器 ---")
    demo_decorator()
    print("--- 4. 上下文管理器 ---")
    demo_context_manager()
    print("--- 5. 并发 ---")
    demo_concurrency()
    print("--- 6. 枚举 ---")
    demo_enum()
    print("--- 7. 数据类 ---")
    demo_dataclass()
    print("--- 8. 类型提示 ---")
    demo_typing()


if __name__ == "__main__":
    main()
    print("=== 11 高级特性 结束 ===")
