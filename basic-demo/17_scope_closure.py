"""
===== 第17课：作用域、闭包与装饰器 =====
对标 Java 的 AOP / 无闭包（lambda 只能捕获 final 变量）
"""

print('⚠️ 本课会故意触发若干异常用于教学演示，它们都会被 try/except 捕获，控制台出现 Error / Exception 字样属正常现象，脚本退出码为 0\n')

import functools
import time

# ==================== 一、LEGB 作用域规则 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: 作用域由 {} 决定，是「块级作用域」
# Java: 查找顺序 = 当前代码块 → 外层代码块 → 类字段 → 静态字段 → 都没有则编译报错
# Python: 查找顺序固定为 L → E → G → B，只在「读取」时逐级往外找，先找到谁就用谁
#   L = Local      当前函数内部
#   E = Enclosing  外层函数内部（闭包）
#   G = Global     当前模块（这个 .py 文件）的全局命名空间
#   B = Builtin    Python 内置命名空间（len / print / sum / range ...）

# --- 四级同名的完整演示：读取时从最内层开始逐级往外找 ---
x = "G-模块全局"                       # G 层


def outer_level():
    x = "E-外层函数"                   # E 层
    def inner_level():
        x = "L-本层函数"               # L 层
        print("inner 读到:", x)        # L 层有，就用 L 层，不再往外找
    inner_level()
    print("outer 读到:", x)            # E 层有，就用 E 层

outer_level()
print("模块层读到:", x)                # G 层
# 输出值: inner 读到: L-本层函数
# 输出值: outer 读到: E-外层函数
# 输出值: 模块层读到: G-模块全局

# --- 逐级往外找：把本层的 x 删掉，就会去 E 层拿 ---
def outer_no_local():
    x = "E-外层函数"
    def inner_no_local():
        # 本层没有赋值，读取时往外找 → E 层
        print("逐级外找:", x)          # 拿到 E 层的值
    inner_no_local()

outer_no_local()
# 输出值: 逐级外找: E-外层函数

# --- 找到 B 层（内置）---
def use_builtin():
    # L 层没有 len，E 层没有，G 层没有 → 到 B 层拿到内置 len
    print("内置 len:", len("abcd"))

use_builtin()
# 输出值: 内置 len: 4

# ⚠️ 关键差异：Python 没有块级作用域，if / for / while / with 都不产生新作用域
# Java:
#   for (int i = 0; i < 3; i++) { }   // i 出了循环就不可见
#   if (true) { int t = 1; }          // t 出了 if 就不可见
if True:
    block_var = "我在 if 里定义"

for i in range(3):
    loop_var = i

print(block_var)                       # if 外依然可见
print(loop_var)                        # for 外依然可见
print(i)                               # 循环变量也泄漏到外层
# 输出值: 我在 if 里定义
# 输出值: 2
# 输出值: 2

# ⚠️ 唯一例外：推导式（comprehension）在 Python 3 里有自己的作用域
squares = [n for n in range(3)]
print(squares)
try:
    print(n)                           # 推导式的循环变量 n 在外面不存在
except NameError as e:
    print("NameError:", e)
# 输出值: [0, 1, 2]
# 输出值: NameError: name 'n' is not defined

# ==================== 二、global 与 nonlocal ====================
# ⭐⭐ 常用 —— 经常用
# Java: 没有这个问题，类字段天然可读写
# Python: 函数内「赋值」默认创建局部变量，除非显式声明 global / nonlocal

# --- 反例：不写 global，直接改全局变量 → UnboundLocalError ---
counter = 0

def bad_increment():
    try:
        # Python 看到函数内有对 counter 的「赋值」，就认定 counter 是局部变量；
        # 但这一行又要先读取 counter → 局部变量还没赋值 → UnboundLocalError
        counter = counter + 1
    except UnboundLocalError as e:
        print("UnboundLocalError:", e)

bad_increment()
print("全局 counter 没变:", counter)
# 输出值: UnboundLocalError: cannot access local variable 'counter' where it is not associated with a value
# 输出值: 全局 counter 没变: 0

# --- 正例：加 global 声明 ---
def good_increment():
    global counter                     # 声明：下面操作的是模块级全局变量
    counter += 1

good_increment()
good_increment()
print("全局 counter 变了:", counter)
# 输出值: 全局 counter 变了: 2

# --- 只读不写时，不需要 global ---
def read_only():
    print("只读全局 counter:", counter)   # 只读取，不会报错

read_only()
# 输出值: 只读全局 counter: 2

# --- nonlocal：修改「外层函数」的变量（只用于嵌套函数）---
def outer_nonlocal():
    total = 0                          # 这是 E 层的变量

    def add(amount):
        nonlocal total                 # 声明：操作的是 E 层的 total，不是新建局部变量
        total += amount
        return total

    print("第一次:", add(10))
    print("第二次:", add(5))

outer_nonlocal()
# 输出值: 第一次: 10
# 输出值: 第二次: 15

# ⚠️ nonlocal 只能向上找到「函数作用域」，找不到模块全局：
#    nonlocal 目标若不存在 → SyntaxError: no binding for nonlocal 'xxx' found
#    global 与 nonlocal 都不能用于模块顶层

# ==================== 三、闭包（Closure）====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# 闭包 = 内层函数 + 定义时记住的外层环境（自由变量）
# Java: lambda / 匿名内部类只能捕获 effectively final 的变量，捕获后不能修改；
#       想要「可变的捕获状态」，Java 只能靠类字段或 AtomicInteger 之类的容器绕过去。
# Python: 闭包直接持有变量本身，配合 nonlocal 可读可写 —— 这是 Python 更灵活的地方。

def make_counter():
    """计数器工厂：每次调用返回一个独立计数的函数"""
    count = 0                          # 被内层函数捕获的自由变量

    def increment():
        nonlocal count                 # 关键：让闭包能「写」外层变量
        count += 1
        return count

    return increment                   # 返回函数本身，不是调用结果

c1 = make_counter()
c2 = make_counter()
print(c1())                            # 1
print(c1())                            # 2
print(c1())                            # 3
print(c2())                            # 1 ← 全新独立的一份状态
# 输出值: 1
# 输出值: 2
# 输出值: 3
# 输出值: 1

# --- 证明状态确实被保留在函数对象里：查看 __closure__ ---
print("闭包捕获数量:", len(c1.__closure__))
print("闭包里的值:", c1.__closure__[0].cell_contents)
print("c2 闭包里的值:", c2.__closure__[0].cell_contents)
# 输出值: 闭包捕获数量: 1
# 输出值: 闭包里的值: 3
# 输出值: c2 闭包里的值: 1

# --- 工厂函数：定制化函数（典型闭包用途）---
def make_multiplier(factor):
    """返回一个「乘以 factor」的函数"""
    def multiply(value):
        return value * factor          # factor 来自闭包，不是参数
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)
print("double(5):", double(5))         # 10
print("triple(5):", triple(5))         # 15
print("double 捕获的 factor:", double.__closure__[0].cell_contents)   # 2
# 输出值: double(5): 10
# 输出值: triple(5): 15
# 输出值: double 捕获的 factor: 2

# Java 等价写法（必须是 final，且无法在闭包里修改）：
#   int factor = 2;
#   Function<Integer, Integer> double = v -> v * factor;   // factor 必须 effectively final

# ==================== 四、闭包陷阱：循环变量捕获 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# 闭包捕获的是「变量本身」，不是「变量的值」。
# for 循环只有一个 i，所有 lambda 捕获的是同一个 i，循环结束后 i 停在最后一个值。

# --- 错误示范 ---
funcs_bad = []
for i in range(3):
    funcs_bad.append(lambda: i)        # 每个 lambda 都捕获同一个变量 i
print("错误结果:", [f() for f in funcs_bad])
# 输出值: 错误结果: [2, 2, 2]

# --- 修正方式 1：默认参数绑定（在定义时把当前值「焊死」成默认值）---
funcs_default = []
for i in range(3):
    funcs_default.append(lambda i=i: i)   # i=i 在定义时求值，立刻绑定当前值
print("默认参数修正:", [f() for f in funcs_default])
# 输出值: 默认参数修正: [0, 1, 2]

# --- 修正方式 2：functools.partial 固定参数 ---
def tag(index, prefix):
    return f"{prefix}{index}"

funcs_partial = [functools.partial(tag, i, "第") for i in range(3)]
print("partial 修正:", [f() for f in funcs_partial])
# 输出值: partial 修正: ['第0', '第1', '第2']

# --- 修正方式 3：再套一层工厂函数（用参数把值带进新的作用域）---
def make_printer(value):
    def printer():
        return value
    return printer

funcs_factory = [make_printer(i) for i in range(3)]
print("工厂函数修正:", [f() for f in funcs_factory])
# 输出值: 工厂函数修正: [0, 1, 2]

# Java 对照：Java 的 lambda 要求捕获变量 effectively final，
# 所以 for (int i...) 里写 lambda 必须再声明一个 final 局部变量，
# 反而天然避开了这个坑，但也因此不能在闭包里修改外部变量。
#   for (int i = 0; i < 3; i++) {
#       final int v = i;                     // ← 必须这样写才能编译通过
#       list.add(() -> v);
#   }

# ==================== 五、functools 工具箱 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: java.util.function + Stream API 里没有对口工具，很多要自己写

# --- 1) functools.wraps：为什么必需 ---
# 装饰器返回的是 wrapper，如果不加 wraps，原函数的元信息（__name__ / __doc__ / __module__）全丢

def no_wraps(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def with_wraps(func):
    @functools.wraps(func)             # 把 func 的元信息复制到 wrapper 上
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@no_wraps
def add_plain(a, b):
    """两数相加（无 wraps）"""
    return a + b

@with_wraps
def add_wrapped(a, b):
    """两数相加（有 wraps）"""
    return a + b

print("不加 wraps 的 __name__:", add_plain.__name__)
print("不加 wraps 的 __doc__:", add_plain.__doc__)
print("加 wraps 的 __name__:", add_wrapped.__name__)
print("加 wraps 的 __doc__:", add_wrapped.__doc__)
print("有无 __wrapped__:", hasattr(add_plain, "__wrapped__"), hasattr(add_wrapped, "__wrapped__"))
# 输出值: 不加 wraps 的 __name__: wrapper
# 输出值: 不加 wraps 的 __doc__: None
# 输出值: 加 wraps 的 __name__: add_wrapped
# 输出值: 加 wraps 的 __doc__: 两数相加（有 wraps）
# 输出值: 有无 __wrapped__: False True

# 实际影响：日志/文档/Swagger/调试栈里看到的函数名全变成 wrapper，排查极其痛苦
# 链路：__wrapped__ 让 inspect.signature()、inspect.unwrap() 能穿透装饰器拿到原函数

# --- 2) functools.lru_cache：记忆化（≈ Spring @Cacheable / 手写 HashMap 缓存）---
# ⭐⭐⭐ 必会
slow_calls = 0

def fib_slow(n):
    """朴素递归斐波那契：指数级重复计算"""
    global slow_calls
    slow_calls += 1
    if n < 2:
        return n
    return fib_slow(n - 1) + fib_slow(n - 2)

print("fib_slow(25):", fib_slow(25))
print("fib_slow 调用次数:", slow_calls)
# 输出值: fib_slow(25): 75025
# 输出值: fib_slow 调用次数: 242785

fast_calls = 0

@functools.lru_cache(maxsize=None)     # maxsize=None 表示不限容量；functools.cache 等价写法（3.9+）
def fib_fast(n):
    """带缓存的斐波那契：同一个 n 只算一次"""
    global fast_calls
    fast_calls += 1
    if n < 2:
        return n
    return fib_fast(n - 1) + fib_fast(n - 2)

print("fib_fast(25):", fib_fast(25))
print("fib_fast 调用次数:", fast_calls)
print("缓存统计:", fib_fast.cache_info())
# 输出值: fib_fast(25): 75025
# 输出值: fib_fast 调用次数: 26
# 输出值: 缓存统计: CacheInfo(hits=23, misses=26, maxsize=None, currsize=26)

# Java 对照：
#   Spring:  @Cacheable(value = "fib", key = "#n")   ← 需要 Spring 容器 + 缓存实现
#   手写:    Map<Integer, Long> cache = new HashMap<>();  if (cache.containsKey(n)) return cache.get(n);
#   Python 一行 @functools.lru_cache 搞定，且线程安全（内部有锁）

# ⚠️ 限制：参数必须可哈希（hashable），list / dict / set 不能直接用
@functools.lru_cache(maxsize=None)
def sum_items(items):
    return sum(items)

print("元组参数 OK:", sum_items((1, 2, 3)))
try:
    sum_items([1, 2, 3])               # list 不可哈希
except TypeError as e:
    print("TypeError:", e)
# 输出值: 元组参数 OK: 6
# 输出值: TypeError: unhashable type: 'list'

# --- 3) functools.partial：固定部分参数（Java 没有对应，只能写 lambda）---
# ⭐⭐ 常用
def power(base, exponent):
    return base ** exponent

square = functools.partial(power, exponent=2)          # 固定关键字参数
cube_of_two = functools.partial(power, 2, 3)           # 固定位置参数
print("square(5):", square(5))
print("cube_of_two():", cube_of_two())
# 输出值: square(5): 25
# 输出值: cube_of_two(): 8

# Java 对照：无对口 API，只能写闭包
#   Function<Integer, Integer> square = x -> power(x, 2);

# --- 4) functools.reduce：≈ Java Stream.reduce ---
# ⭐⭐ 常用
# Java: nums.stream().reduce(0, Integer::sum);
nums = [1, 2, 3, 4, 5]
print("求和:", functools.reduce(lambda a, b: a + b, nums))
print("求积:", functools.reduce(lambda a, b: a * b, nums))
print("带初始值 100:", functools.reduce(lambda a, b: a + b, nums, 100))
print("求最大值:", functools.reduce(lambda a, b: a if a > b else b, nums))
# 输出值: 求和: 15
# 输出值: 求积: 120
# 输出值: 带初始值 100: 115
# 输出值: 求最大值: 5

# --- 5) functools.total_ordering（第16课已讲，此处仅提及）---
# 只实现 __eq__ + __lt__，自动补齐 __le__ / __gt__ / __ge__
# Java 对照：Comparable 接口要手写 compareTo，其他比较靠默认实现

# ==================== 六、装饰器进阶 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档

# --- 1) 不带参数的装饰器：两层结构 ---
# ⭐⭐⭐
def simple_log(func):
    @functools.wraps(func)             # ← 内层 wrapper 上加 wraps
    def wrapper(*args, **kwargs):
        print(f"[log] 调用 {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@simple_log
def say_hi(name):
    return f"Hi, {name}"

print(say_hi("Tom"))
# 输出值: [log] 调用 say_hi
# 输出值: Hi, Tom

# --- 2) 带参数的装饰器：三层嵌套（工厂 → 装饰器 → 包装器）---
# ⭐⭐⭐
# Java 对照：≈ @Transactional(timeout = 3) / @Retryable(maxAttempts = 3)，
#            Java 靠注解属性 + 容器解析，Python 直接用函数参数
def repeat(times):
    """最外层：装饰器工厂，负责接收装饰器自己的参数"""
    def decorator(func):
        """中间层：真正的装饰器，接收被装饰的函数"""
        @functools.wraps(func)         # ← wraps 永远加在最内层 wrapper 上
        def wrapper(*args, **kwargs):
            """最内层：包装器，负责增强逻辑"""
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)                             # 等价于 say_hi_3 = repeat(3)(say_hi_3)
def greet_once(name):
    print(f"你好, {name}")
    return name

print("返回值:", greet_once("Alice"))
# 输出值: 你好, Alice
# 输出值: 你好, Alice
# 输出值: 你好, Alice
# 输出值: 返回值: Alice

# 写法差异总结：
#   不带参数：      def deco(func)                     → 两层，@deco
#   带参数：        def deco(*deco_args) → def _(func) → 三层，@deco(args)
#   @functools.wraps 永远加在「最内层的 wrapper」上，与层数无关

# --- 3) 多个装饰器堆叠：装饰顺序自下而上，执行顺序自上而下 ---
# ⭐⭐⭐
def deco_a(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("[A] 进入")
        result = func(*args, **kwargs)
        print("[A] 离开")
        return result
    return wrapper

def deco_b(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("[B] 进入")
        result = func(*args, **kwargs)
        print("[B] 离开")
        return result
    return wrapper

@deco_a                                # 后应用（外层）
@deco_b                                # 先应用（内层）
def stacked():
    print("[业务] 执行")

# 装饰顺序（定义时）：先 deco_b 包住 stacked，再 deco_a 包住结果
# 等价于：stacked = deco_a(deco_b(stacked))
print("函数名仍是:", stacked.__name__)
stacked()
# 输出值: 函数名仍是: stacked
# 输出值: [A] 进入
# 输出值: [B] 进入
# 输出值: [业务] 执行
# 输出值: [B] 离开
# 输出值: [A] 离开

# Java 对照：≈ Spring AOP 多切面叠加，@Order 控制顺序；Python 靠「离函数近的先执行」

# --- 4) 类装饰器：用 __call__ 实现（⭐ 了解，用到再查）---
# ⭐ 了解
# Java 对照：Java 注解不能实例化为「可调用的包装对象」，必须靠反射 + 动态代理
class CountCalls:
    """类装饰器：实例本身可调用，因此可以直接替换被装饰函数"""

    def __init__(self, func):
        self.func = func
        self.count = 0
        functools.update_wrapper(self, func)     # 类装饰器保持元信息

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"[第 {self.count} 次调用]")
        return self.func(*args, **kwargs)

@CountCalls
def ping():
    return "pong"

print(ping())
print(ping())
print("总调用次数:", ping.count)
print("函数名仍是:", ping.__name__)
# 输出值: [第 1 次调用]
# 输出值: pong
# 输出值: [第 2 次调用]
# 输出值: pong
# 输出值: 总调用次数: 2
# 输出值: 函数名仍是: ping

# --- 5) 实战一：计时装饰器（≈ Spring @Around 记录耗时）---
# ⭐⭐⭐
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()          # perf_counter 精度高于 time.time()
        try:
            return func(*args, **kwargs)
        finally:
            # Java: long cost = System.nanoTime() - start;
            cost_ms = (time.perf_counter() - start) * 1000
            print(f"[timer] {func.__name__} 耗时 {cost_ms:.2f} ms")
    return wrapper

@timer
def busy_task(n):
    time.sleep(0.01)
    return sum(range(n))

print("结果:", busy_task(1000))
# 输出值: [timer] busy_task 耗时 10.xx ms（具体毫秒数每次运行不同，此处不固定）
# 输出值: 结果: 499500

# --- 6) 实战二：重试装饰器（异常重试 + 次数 + 延迟）---
# ⭐⭐⭐
# Java 对照：Spring Retry 的 @Retryable / Resilience4j 的 @Retry
def retry(times=3, delay=0.0, exceptions=(Exception,)):
    """times: 最大尝试次数；delay: 每次重试间隔秒数；exceptions: 需要重试的异常类型"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    print(f"  第 {attempt} 次尝试失败: {e}")
                    if attempt < times and delay > 0:
                        time.sleep(delay)
            print(f"  重试 {times} 次仍然失败")
            raise last_exc
        return wrapper
    return decorator

flaky_attempts = 0

@retry(times=3, delay=0.01)
def flaky_service():
    """前两次失败，第三次成功"""
    global flaky_attempts
    flaky_attempts += 1
    if flaky_attempts < 3:
        raise ValueError(f"模拟网络抖动 {flaky_attempts}")
    return "调用成功"

print("最终结果:", flaky_service())
# 输出值:   第 1 次尝试失败: 模拟网络抖动 1
# 输出值:   第 2 次尝试失败: 模拟网络抖动 2
# 输出值: 最终结果: 调用成功

@retry(times=2)
def always_fail():
    raise RuntimeError("服务永久不可用")

try:
    always_fail()
except RuntimeError as e:
    print("最终抛出异常:", e)
# 输出值:   第 1 次尝试失败: 服务永久不可用
# 输出值:   第 2 次尝试失败: 服务永久不可用
# 输出值:   重试 2 次仍然失败
# 输出值: 最终抛出异常: 服务永久不可用

# --- 7) 实战三：手写缓存装饰器（理解 lru_cache 原理）---
# ⭐⭐⭐
def memoize(func):
    """简易记忆化装饰器：内部就是一张 dict"""
    cache = {}                              # 闭包持有，等价于 Java 的 Map<参数, 结果>

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 参数必须可哈希才能当 dict 的 key
        key = args + tuple(sorted(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)   # 未命中：真正执行并写入缓存
        return cache[key]

    wrapper.cache = cache                   # 暴露缓存，便于查看
    return wrapper

memo_calls = 0

@memoize
def fib_memo(n):
    global memo_calls
    memo_calls += 1
    if n < 2:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)

print("fib_memo(20):", fib_memo(20))
print("真实调用次数:", memo_calls)
print("缓存条目数:", len(fib_memo.cache))
print("重复调用命中缓存:", fib_memo(20), "调用次数仍为", memo_calls)
# 输出值: fib_memo(20): 6765
# 输出值: 真实调用次数: 21
# 输出值: 缓存条目数: 21
# 输出值: 重复调用命中缓存: 6765 调用次数仍为 21

# Java 对照（手写缓存）：
#   private final Map<Integer, Long> cache = new HashMap<>();
#   public long fib(int n) { return cache.computeIfAbsent(n, this::fib); }
# Python 的 @memoize 把「缓存 + 装饰」做成语言级复用，任何函数一行接入

# --- 8) 装饰器能力对比总结 ---
# Java: @Transactional / @Around / @Cacheable 都只是「元数据」，必须有 Spring 容器
#       （或 APT/字节码增强）在运行时生成代理类才生效，脱离容器注解等于注释。
# Python: 装饰器是语法糖 func = decorator(func)，纯语言机制，
#         不需要容器、不需要代理、不需要反射，任何函数随时可装饰。

print("=== 17 作用域、闭包与装饰器 结束 ===")
