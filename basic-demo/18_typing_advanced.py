"""
===== 第18课：类型提示进阶 =====
对标 Java 的泛型 / 注解，但运行时完全不强制
"""

print('⚠️ 本课会故意触发若干异常用于教学演示，它们都会被 try/except 捕获，控制台出现 Error / Exception 字样属正常现象，脚本退出码为 0\n')

# ==================== 零、核心认知：类型提示运行时完全不生效 ====================
# ⭐⭐⭐ 必会
#
# Java: 泛型是"编译期强制"的 —— List<String> 里塞 Integer 直接编译失败；
#       泛型信息确实会在编译后被擦除，但擦除发生在"检查之后"，
#       能跑起来的字节码里已经保证了类型正确。
#
# Python: 连"擦除"都谈不上 —— 解释器压根不读类型提示。
#       它只是挂在函数上的一段普通数据（__annotations__ 字典），
#       写错类型照样跑，不报错、不警告、不降速。
#
# 结论：Python 的类型提示是给 mypy / pyright / IDE 看的。
#   必须配静态检查工具，它才有价值：
#     mypy    18_typing_advanced.py
#     pyright 18_typing_advanced.py
#   （本课只演示运行时行为，不实际执行上面两条命令）

# Java: public String add(int a, int b) { return a + b; }  ← 返回 int 会编译报错
def add(a: int, b: int) -> str:
    """声明参数 int、返回 str，实际返回 int，且允许传 str —— 解释器全都不管"""
    return a + b

print(add(1, 2))          # 3
print(type(add(1, 2)))    # <class 'int'>  ← 声明的是 str，实际是 int，没人管
print(add("1", "2"))      # 12  ← 声明参数是 int，传 str 照样拼接成功

# 运行时可以"读"到注解（反射），这也是 ORM / 参数校验框架的原理
# Java: 相当于 method.getAnnotation() / getGenericParameterTypes()
from typing import get_type_hints

def greet(name: str, age: int = 18) -> str:
    """打招呼"""
    return f"{name}-{age}"

print(greet.__annotations__)
# {'name': <class 'str'>, 'age': <class 'int'>, 'return': <class 'str'>}

# get_type_hints 比 __annotations__ 更强：会把字符串注解解析成真正的类型对象
# 注意：多了 'return' 键，且顺序按定义顺序
print(get_type_hints(greet))
# {'name': <class 'str'>, 'age': <class 'int'>, 'return': <class 'str'>}

# ==================== 一、基础与现代化写法 ====================
# ⭐⭐⭐ 必会
# Java: public List<String> names = new ArrayList<>();
#       public Map<String, Integer> scores = new HashMap<>();

# --- 旧写法：从 typing 里 import 大写容器类型（3.9 之前唯一选择，现在不推荐）---
from typing import List, Dict, Tuple, Set

def old_style(names: List[str], scores: Dict[str, int]) -> Tuple[int, str]:
    return len(names), str(scores)

# --- 现代写法（3.9+）：直接用内置类型当泛型，不用 import ---
def new_style(names: list[str], scores: dict[str, int]) -> tuple[int, str]:
    return len(names), str(scores)

print(old_style(["a", "b"], {"a": 1}))    # (2, "{'a': 1}")
print(new_style(["a", "b"], {"a": 1}))    # (2, "{'a': 1}")

# 为什么现在推荐小写内置泛型？
# 1) 不用 import，少一行；2) 运行时就是内置类型的泛型别名，行为更一致
print(type(list[str]))      # <class 'types.GenericAlias'>
print(type(List[str]))      # <class 'typing._GenericAlias'>
print(list[str])            # list[str]
print(List[str])            # typing.List[str]

# set / tuple 同理
# Java: Set<Integer>、Map.Entry 等
tags: set[int] = {1, 2, 3}
point: tuple[int, str] = (1, "a")
print(tags)                 # {1, 2, 3}
print(point)                # (1, 'a')

# 元组的"定长异类型"写法：tuple[int, str] 表示第一个是 int、第二个是 str
# 而 tuple[int, ...] 表示"任意多个 int"
def sum_all(nums: tuple[int, ...]) -> int:
    return sum(nums)

print(sum_all((1, 2, 3, 4)))    # 10

# --- 嵌套泛型：list[dict[str, list[int]]] ---
# Java: List<Map<String, List<Integer>>> —— 括号地狱，Python 一样躲不掉
def total_by_key(rows: list[dict[str, list[int]]]) -> dict[str, int]:
    """把多行 {键: [数值...]} 按同名键累加"""
    result: dict[str, int] = {}
    for row in rows:
        for key, values in row.items():
            result[key] = result.get(key, 0) + sum(values)
    return result

data: list[dict[str, list[int]]] = [{"a": [1, 2], "b": [3]}, {"a": [10], "b": [4, 5]}]
print(total_by_key(data))       # {'a': 13, 'b': 12}

# ==================== 二、可选与联合 ====================
# ⭐⭐⭐ 必会
#
# ⚠️ 最大的认知差异：
#   Java 的 Optional<T> 是一个"容器对象"，包着可能为空的值，要 .get() / .orElse() / .isPresent()
#   Python 的 Optional[X] 只是 X | None 的"别名"，不是容器 —— 值本身就是 None，直接 if 判断
from typing import Optional, Union

# Java: public Optional<String> findUser(int id) { ... }
def find_user(user_id: int) -> Optional[str]:
    if user_id == 1:
        return "Alice"
    return None

print(find_user(1))        # Alice
print(find_user(2))        # None

# --- 3.10+ 新写法：X | None，与 Optional[X] 完全等价 ---
def find_user_v2(user_id: int) -> str | None:
    return "Alice" if user_id == 1 else None

print(find_user_v2(1))     # Alice
print(find_user_v2(9))     # None

# 证明两者是同一个东西（不是两个不同的类型）
print(Optional[str] == str | None)      # True
print(Optional[str])                    # typing.Optional[str]
print(str | None)                       # str | None

# --- Union[A, B] 与 A | B ---
# Java: 没有直接对应，只能靠重载或 Object + instanceof
def to_int(value: Union[int, str]) -> int:
    return int(value)

def to_int_v2(value: int | str | float) -> int:
    return int(value)

print(to_int(5))           # 5
print(to_int("42"))        # 42
print(to_int_v2(3.9))      # 3

# Union 会自动去重、拍平：Union[int, int] 就是 int
print(Union[int, int])     # <class 'int'>

# --- 实际场景：返回值可能为 None 时的签名设计 ---
# Java 习惯：返回 Optional<User>，调用方 .orElse(null)
# Python 习惯：返回 User | None，调用方 if x is None: ...
def find_config(user_id: int) -> dict[str, str] | None:
    db: dict[int, dict[str, str]] = {1: {"host": "127.0.0.1", "port": "3306"}}
    return db.get(user_id)

cfg = find_config(1)
if cfg is not None:
    print(cfg)                  # {'host': '127.0.0.1', 'port': '3306'}
    print(cfg["host"])          # 127.0.0.1

# ⚠️ 别用 if not x 判断 None：0、""、[] 也会被判成假
missing = find_config(999)
print(missing is None)          # True
print(bool(missing))            # False（这里凑巧一致，但值是 0 时 if not x 就会误判）

# ==================== 三、Callable ====================
# ⭐⭐ 常用
# Java: Function<Integer, String>、BiFunction<Integer, String, Boolean>
#       Runnable、Supplier<String>
#
# 写法：Callable[[参数类型列表], 返回类型]
#   Callable[[], None]        ≈ Java Runnable
#   Callable[[], str]         ≈ Java Supplier<String>
#   Callable[[int], str]      ≈ Java Function<Integer, String>
#   Callable[[int, str], bool] ≈ Java BiFunction<Integer, String, Boolean>
#   Callable[..., int]        =  参数任意（Java 无对应）
from typing import Callable

# Java: public boolean check(BiFunction<Integer, String, Boolean> f, int n, String s)
def check(predicate: Callable[[int, str], bool], num: int, text: str) -> bool:
    return predicate(num, text)

def is_long_enough(n: int, s: str) -> bool:
    return len(s) > n

print(check(is_long_enough, 3, "python"))                  # True
print(check(is_long_enough, 10, "python"))                 # False
print(check(lambda n, s: s.startswith("p"), 0, "python"))  # True

# 用在高阶函数签名上：接收函数、返回列表
# Java: Stream 的 map 参数 Function<T, R>
def apply_all(func: Callable[[int], int], values: list[int]) -> list[int]:
    return [func(v) for v in values]

print(apply_all(lambda x: x * x, [1, 2, 3]))    # [1, 4, 9]
print(apply_all(abs, [-1, -2, 3]))              # [1, 2, 3]

# 参数个数不确定时用省略号
# Java: 只能靠 Object... + 反射
def call_any(func: Callable[..., int], *args: object) -> int:
    return func(*args)

print(call_any(len, [1, 2, 3]))    # 3
print(call_any(max, 5, 9, 2))      # 9

# 3.9+ 也可以从 collections.abc 拿 Callable，对类型检查器来说两者等价，
# 但运行时是两个不同的对象（别用 == 去比较类型提示，永远别这么干）
from collections.abc import Callable as AbcCallable
print(Callable[[int], str] == AbcCallable[[int], str])    # False
print(AbcCallable[[int], str])                            # collections.abc.Callable[[int], str]

# ==================== 四、字面量与字典结构 ====================
# ⭐⭐ 常用
from typing import Literal, TypedDict, NotRequired

# --- Literal：把取值限定在几个字面量里 ---
# Java: public enum Mode { R, W, A }  然后参数类型写 Mode
# 区别：Literal 只是"裸值"，没有枚举的方法、不能遍历、没有 name/value
#       需要枚举行为时还是用 Enum（第11课）或 StrEnum
def open_file(path: str, mode: Literal["r", "w", "a"]) -> str:
    return f"以 {mode} 模式打开 {path}"

print(open_file("data.txt", "r"))      # 以 r 模式打开 data.txt
# 下面这行 mypy 会报错，但解释器照跑 —— 运行时没有任何校验
print(open_file("data.txt", "x"))      # 以 x 模式打开 data.txt

# Literal 也可以是 int / bool
def set_level(level: Literal[1, 2, 3]) -> str:
    return f"等级 {level}"

print(set_level(2))                    # 等级 2

# --- TypedDict：给 dict 加结构 ---
# Java: public record UserDTO(long id, String name, boolean vip) {}
# 区别：Java record 有真实的字段、getter、不可变；TypedDict 运行时就是普通 dict
class UserDTO(TypedDict):
    """用户传输对象（仅类型层面有结构）"""
    id: int
    name: str
    vip: bool

user: UserDTO = {"id": 1, "name": "Alice", "vip": True}
print(user)                       # {'id': 1, 'name': 'Alice', 'vip': True}
print(user["name"])               # Alice
print(type(user))                 # <class 'dict'>   ← 运行时就是普通 dict
print(isinstance(user, dict))     # True

# 不做任何校验：少写字段、写错键，运行时都不报错（mypy 才会报）
incomplete: UserDTO = {"id": 2, "name": "Bob"}   # mypy: 缺少 vip
print(incomplete)                 # {'id': 2, 'name': 'Bob'}

# total=False：所有键都可选（3.11+ 更推荐 NotRequired，粒度更细）
class PartialUser(TypedDict, total=False):
    name: str
    age: int

p1: PartialUser = {"name": "Tom"}
print(p1)                         # {'name': 'Tom'}

class Article(TypedDict):
    title: str
    tags: NotRequired[list[str]]  # 只有这个键可选

a1: Article = {"title": "Python 类型提示"}
a2: Article = {"title": "Python 类型提示", "tags": ["typing", "mypy"]}
print(a1)                         # {'title': 'Python 类型提示'}
print(a2)                         # {'title': 'Python 类型提示', 'tags': ['typing', 'mypy']}

# ==================== 五、Protocol —— 结构化子类型 ====================
# ⭐⭐ 常用
#
# Java: interface Greeter { String greet(); } —— 类必须写 implements Greeter，否则编译不过
# Python: Protocol 只看"有没有这些方法"，不需要显式继承
#         = 鸭子类型（duck typing）的类型化表达：
#           "如果它走起来像鸭子、叫起来像鸭子，那它就是鸭子"
from typing import Protocol, runtime_checkable

class Greeter(Protocol):
    """协议：只要有 greet() -> str 就算满足（这里的 ... 是声明，不是省略实现）"""
    def greet(self) -> str:
        ...

class Chinese:
    """完全没继承 Greeter，但满足协议"""
    def greet(self) -> str:
        return "你好"

class Robot:
    """毫不相干的另一个类，同样满足协议"""
    def greet(self) -> str:
        return "BEEP"

# Java: public String sayHello(Greeter g) —— 传进来的必须 implements Greeter
def say_hello(g: Greeter) -> str:
    return g.greet()

print(say_hello(Chinese()))    # 你好
print(say_hello(Robot()))      # BEEP

# 显式继承 Protocol 也可以（这时才像 Java 的 implements），但通常没必要
class English(Greeter):
    def greet(self) -> str:
        return "Hello"

print(say_hello(English()))    # Hello

# --- runtime_checkable：让 Protocol 支持 isinstance 运行时检查 ---
# ⚠️ 只检查"方法名存不存在"，不检查签名和返回类型
@runtime_checkable
class HasName(Protocol):
    def name(self) -> str:
        ...

class Dog:
    def name(self) -> str:
        return "旺财"

class Cat:
    pass    # 没有 name()，不满足协议

print(isinstance(Dog(), HasName))    # True
print(isinstance(Cat(), HasName))    # False

# ==================== 六、泛型 ====================
# ⭐⭐ 常用
from typing import TypeVar, Generic

# --- 旧写法：先定义 TypeVar，再继承 Generic[T] ---
# Java: public class Box<T> { private T value; public T get() { return value; } }
T = TypeVar("T")

class Box(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value

    def __repr__(self) -> str:
        return f"Box({self.value!r})"

print(Box(123))            # Box(123)
print(Box("abc"))          # Box('abc')
print(Box(123).get())      # 123
print(Box[int])            # __main__.Box[int]

# TypeVar 本身在运行时只是个对象，打印出来是 ~T
print(T)                   # ~T

# --- 3.12+ 新语法（PEP 695）：不用先定义 TypeVar，直接写在类名后面 ---
# Java 里没有对应写法，这是 Python 独有的"声明式泛型参数"
class NewBox[T]:
    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value

    def __repr__(self) -> str:
        return f"NewBox({self.value!r})"

print(NewBox(3.14))            # NewBox(3.14)
print(NewBox([1, 2]).get())    # [1, 2]
print(NewBox.__type_params__)  # (T,)

# --- 上界：Java 的 <T extends X>，Python 用 bound= ---
# Java: public <T extends Animal> String speak(T a)
class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def sound(self) -> str:
        return "..."

class Dog(Animal):
    def sound(self) -> str:
        return "汪汪"

AnimalT = TypeVar("AnimalT", bound=Animal)

def speak(animal: AnimalT) -> str:
    return f"{animal.name}: {animal.sound()}"

print(speak(Dog("旺财")))      # 旺财: 汪汪
print(speak(Animal("未知")))   # 未知: ...

# PEP 695 的新语法里，上界直接写成 T: Animal
class Kennel[PetT: Animal]:
    def __init__(self) -> None:
        self.pets: list[PetT] = []

    def add(self, pet: PetT) -> None:
        self.pets.append(pet)

    def count(self) -> int:
        return len(self.pets)

kennel: Kennel[Dog] = Kennel()
kennel.add(Dog("小黑"))
kennel.add(Dog("小白"))
print(kennel.count())          # 2

# --- 约束（constraints）：只能是列出的这几个类型之一 ---
# Java 没有直接对应，只能靠重载或 <T extends CharSequence & Serializable>
# 注意约束和上界的区别：约束是"枚举白名单"，上界是"必须是子类"
StrOrBytes = TypeVar("StrOrBytes", str, bytes)

def length_of(value: StrOrBytes) -> int:
    return len(value)

print(length_of("abc"))        # 3
print(length_of(b"abcd"))      # 4

# ==================== 七、重载 @overload ====================
# ⭐⭐ 常用
#
# ⚠️⚠️ 和 Java 的重载是"两回事"，千万不要类比自己骗自己：
#   Java: 编译期确定签名 + 运行时按参数类型"动态派发"，class 文件里真有多个方法
#   Python: @overload 只是给类型检查器看的"声明"，运行时被最后那个真实实现直接覆盖，
#           def 语句执行了 3 次，但函数名只指向最后一个；必须自己 if isinstance 分支
from typing import overload, get_overloads

@overload
def parse(value: int) -> str: ...

@overload
def parse(value: str) -> int: ...

# ↓ 这个才是真正的实现，前两个在运行时已经不存在了
def parse(value: int | str) -> str | int:
    if isinstance(value, int):
        return f"int:{value}"
    if isinstance(value, str):
        return len(value)
    raise TypeError(f"不支持的类型: {type(value).__name__}")

print(parse(42))               # int:42
print(parse("hello"))          # 5
print(parse.__name__)          # parse

# 运行时确实只有 1 个实现，但 typing 帮我们把"声明"存了下来，可以数出来
print(len(get_overloads(parse)))    # 2
print([f.__name__ for f in get_overloads(parse)])    # ['parse', 'parse']

# 分支必须自己写，漏了就在运行时炸
try:
    parse(3.14)                # type: ignore[arg-type]
except TypeError as exc:
    print(f"{type(exc).__name__}: {exc}")    # TypeError: 不支持的类型: float

# ==================== 八、其他常用标记 ====================
from typing import Final, ClassVar, Any, Never
from typing import TypeAlias
import json
import warnings

# --- Final：常量 ---
# ⭐ 了解
# Java: public static final int MAX_RETRY = 3;
MAX_RETRY: Final[int] = 3
print(MAX_RETRY)               # 3

# ⚠️ Final 只是给 mypy 看的，运行时照样能改，改完也不报错
MAX_RETRY = 5
print(MAX_RETRY)               # 5

# --- ClassVar：类变量 ---
# ⭐ 了解
# Java: private static String TABLE = "t_user";
# ⚠️ 关键：在 dataclass 里不加 ClassVar，这个字段会被当成实例字段写进 __init__
from dataclasses import dataclass

@dataclass
class Counter:
    count: ClassVar[int] = 0        # 类变量：不进 __init__，不进 __eq__，不进 __repr__
    name: str = "counter"           # 普通字段：进 __init__

print(Counter("c1"))               # Counter(name='c1')
print(Counter.count)               # 0

# --- Any 与 Never ---
# ⭐ 了解
# Java: Object / JsonNode —— 放弃类型检查
def loads_json(raw: str) -> Any:
    """返回值结构不确定时用 Any（能用具体类型就别用 Any）"""
    return json.loads(raw)

print(loads_json('{"a": 1}'))          # {'a': 1}
print(loads_json("[1, 2]")[1])         # 2

# Never（旧名 NoReturn）：永远不会有返回值 —— 一定抛异常或死循环
# Java: 没有对应，Java 编译器不知道 void 方法"永不返回"
def fail(message: str) -> Never:
    raise RuntimeError(message)

try:
    fail("boom")
except RuntimeError as exc:
    print(f"{type(exc).__name__}: {exc}")    # RuntimeError: boom

# --- TypeAlias / type 语句：给复杂类型起别名 ---
# ⭐ 了解
# Java: 没有类型别名，只能再包一个类或用泛型继承
# 旧写法：右边只是普通赋值，mypy 要靠 TypeAlias 才能确定这是别名而非变量
Matrix: TypeAlias = List[List[float]]

# 3.12+ 新写法（PEP 695）：右边是真正的类型别名对象，mypy 会当成独立类型
type Vector = list[float]
type Handler = Callable[[int], str]

def norm(v: Vector) -> float:
    return sum(x * x for x in v) ** 0.5

print(norm([3.0, 4.0]))        # 5.0
print(Vector)                  # Vector
print(Vector.__value__)        # list[float]
print(Matrix)                  # typing.List[typing.List[float]]

# --- @deprecated（3.13 新增）---
# ⭐ 了解
# Java: @Deprecated 注解，编译器会警告
from warnings import deprecated

@deprecated("请改用 new_api()")
def old_api() -> str:
    return "old"

# 装饰器只负责在"被调用时"发一条 DeprecationWarning，不阻止调用
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    print(old_api())                       # old

print(len(caught))                         # 1
print(caught[0].category.__name__)         # DeprecationWarning
print(old_api.__deprecated__)              # 请改用 new_api()

# ==================== 九、dataclass 进阶 ====================
# ⭐⭐⭐ 必会
# 基础 @dataclass 第11课已讲（自动生成 __init__ / __repr__ / __eq__），这里只讲进阶
from dataclasses import dataclass, field, fields, asdict

# --- 可变默认值陷阱（呼应第15课）---
# Java: 字段初始化 new ArrayList<>() 每个实例都新建，天然没这个问题
# ❌ 普通类：默认值在函数定义时创建一次，所有实例共享同一个 list
class BadTags:
    def __init__(self, tags: list[str] = []) -> None:
        self.tags = tags

b1, b2 = BadTags(), BadTags()
b1.tags.append("x")
print(b1.tags)                 # ['x']
print(b2.tags)                 # ['x']  ← 被污染了！

# ❌ dataclass 里写可变默认值：连类都定义不出来，装饰器当场抛异常
try:
    @dataclass
    class BadTags2:
        tags: list[str] = []
except ValueError as exc:
    print(f"{type(exc).__name__}: {exc}")
    # ValueError: mutable default <class 'list'> for field tags is not allowed: use default_factory

# ✅ 正确姿势：field(default_factory=list)
@dataclass
class GoodTags:
    tags: list[str] = field(default_factory=list)

g1, g2 = GoodTags(), GoodTags()
g1.tags.append("x")
print(g1.tags)                 # ['x']
print(g2.tags)                 # []  ← 互不影响

# --- frozen=True：不可变 dataclass，同时变成可哈希 ---
# Java: record 的字段天然 final，但 record 的 equals/hashCode 也是自动的
@dataclass(frozen=True)
class Money:
    amount: int
    currency: str = "CNY"

m1 = Money(100)
m2 = Money(100)
print(m1)                              # Money(amount=100, currency='CNY')
print(m1 == m2)                        # True
print(hash(m1) == hash(m2))            # True  ← 可哈希，能进 set、能当 dict 的键
print({m1, m2})                        # {Money(amount=100, currency='CNY')}

# 改字段会抛异常（FrozenInstanceError 是 AttributeError 的子类）
try:
    m1.amount = 200                # type: ignore[misc]
except AttributeError as exc:
    print(f"{type(exc).__name__}: {exc}")    # FrozenInstanceError: cannot assign to field 'amount'

# --- order=True：自动生成 __lt__ / __le__ / __gt__ / __ge__ ---
# Java: record 不会自动实现 Comparable，要自己写 compareTo
@dataclass(order=True)
class Version:
    major: int
    minor: int

print(Version(1, 2) < Version(1, 10))          # True
print(Version(2, 0) > Version(1, 9))           # True
print(Version(1, 2) <= Version(1, 2))          # True
print(sorted([Version(2, 0), Version(1, 5)]))  # [Version(major=1, minor=5), Version(major=2, minor=0)]

# compare=False：该字段不参与比较（也不会进 __hash__）
@dataclass(order=True)
class Task:
    priority: int
    name: str = field(compare=False)

print(sorted([Task(2, "写文档"), Task(1, "改 bug")]))
# [Task(priority=1, name='改 bug'), Task(priority=2, name='写文档')]

# --- __post_init__：派生字段 / 参数校验 ---
# Java: record 的紧凑构造器  record Order(...) { Order { if (qty <= 0) throw ...; } }
@dataclass
class Order:
    order_id: str
    unit_price: float
    quantity: int
    total: float = field(init=False)     # init=False：不进 __init__，由 __post_init__ 算出来

    def __post_init__(self) -> None:
        # 参数校验（失败就抛，等价于 Java 构造器里的校验）
        if self.quantity <= 0:
            raise ValueError(f"数量必须大于 0，当前: {self.quantity}")
        # 派生字段
        self.total = round(self.unit_price * self.quantity, 2)

order = Order("SO-001", 19.9, 3)
print(order)                   # Order(order_id='SO-001', unit_price=19.9, quantity=3, total=59.7)

try:
    Order("SO-002", 10.0, 0)
except ValueError as exc:
    print(f"{type(exc).__name__}: {exc}")    # ValueError: 数量必须大于 0，当前: 0

# ⚠️ frozen=True 时不能在 __post_init__ 里直接赋值，要用 object.__setattr__
@dataclass(frozen=True)
class FrozenOrder:
    price: float
    qty: int
    total: float = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "total", round(self.price * self.qty, 2))

print(FrozenOrder(2.5, 4))     # FrozenOrder(price=2.5, qty=4, total=10.0)

# --- 完整业务实体：把上面所有特性串起来 ---
# Java 对照：
#   @dataclass(frozen=True)  ≈ record（字段 final、自动 equals/hashCode/toString）
#   @dataclass(order=True)   ≈ 自己实现 Comparable，按字段定义顺序比较
#   field(default_factory=)  ≈ Lombok @Builder.Default
#   __post_init__            ≈ record 的紧凑构造器 / Lombok 构造器里的校验
#   ClassVar                 ≈ static 字段（不进构造器）
#   slots=True               ≈ 无直接对应（省内存，禁止动态加属性）
@dataclass(frozen=True, order=True, slots=True)
class Employee:
    """员工实体。

    Java: public record Employee(String empNo, String name, double salary,
                                 List<String> skills) {}
    """
    emp_no: str
    name: str
    salary: float
    skills: tuple[str, ...] = ()
    level: int = field(default=1, compare=False, repr=False)          # 不参与比较、不出现在 repr
    history: list[str] = field(default_factory=list, compare=False, repr=False)
    TABLE: ClassVar[str] = "t_employee"                               # 类变量，不是字段

    def __post_init__(self) -> None:
        if not self.emp_no:
            raise ValueError("工号不能为空")
        if self.salary < 0:
            raise ValueError(f"薪资不能为负: {self.salary}")
        if self.level < 1:                                            # 修正非法值
            object.__setattr__(self, "level", 1)

    @property
    def annual_salary(self) -> float:
        """派生属性：不算字段，不进 __init__ / __eq__ / __repr__"""
        return round(self.salary * 12, 2)

    def add_history(self, event: str) -> None:
        """frozen 只锁"属性重新赋值"，不锁"可变对象的内容" """
        self.history.append(event)

e1 = Employee("E001", "张三", 15000.0, ("Java", "Python"), history=["入职"])
e2 = Employee("E002", "李四", 12000.0, level=0)     # level=0 会被 __post_init__ 修正为 1

print(e1)
# Employee(emp_no='E001', name='张三', salary=15000.0, skills=('Java', 'Python'))
print(e2.level)                # 1
print(e1.annual_salary)        # 180000.0
print(e1.name)                 # 张三
print(e1 > e2)                 # False ← order=True 按字段定义顺序比较，先比 emp_no: 'E001' > 'E002' 为假
print(e1.name > e2.name)       # False ← 比到 name 时 '张三' > '李四' 也是假
print(sorted([e2, e1])[0].emp_no)    # E001 ← 排序结果按 emp_no 升序

# frozen=True → 可哈希，能放进 set、当 dict 的键
print(len({e1, e2}))           # 2

# 冻结的只是"字段引用"，可变字段内容仍可改（Java 的 record 里 List 也是同理）
e1.add_history("调薪")
print(e1.history)              # ['入职', '调薪']

# fields()：运行时反射字段（≈ Java 的 getDeclaredFields）
print([f.name for f in fields(Employee)])
# ['emp_no', 'name', 'salary', 'skills', 'level', 'history']

# asdict()：转成普通 dict（≈ Java 的 Jackson 序列化），ClassVar 不会被带进去
print(asdict(e2))
# {'emp_no': 'E002', 'name': '李四', 'salary': 12000.0, 'skills': (), 'level': 1, 'history': []}

print("=== 18 类型提示进阶 结束 ===")   # === 18 类型提示进阶 结束 ===
