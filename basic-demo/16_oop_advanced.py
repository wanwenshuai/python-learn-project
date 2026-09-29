"""
===== 第16课：面向对象进阶 =====
对标 Java 的 static 方法 / 多继承 / 魔法方法

前置：第7课已讲类、继承、@property、__str__/__repr__/__eq__/__add__、ABC。
本课从第7课结束的地方继续，不重复基础内容。
"""

print('⚠️ 本课会故意触发若干异常用于教学演示，它们都会被 try/except 捕获，控制台出现 Error / Exception 字样属正常现象，脚本退出码为 0\n')

import functools
import json
import sys

# ==================== 一、三种方法（本课重点）====================

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: 实例方法 = 普通方法；@classmethod ≈ static 工厂方法但多一个 cls；
#       @staticmethod ≈ Java 的 static 方法（完全等价）

# 三者对照表（背下来）
# +--------------+---------------------+-----------+-----------+-----------+---------------------+
# | 类型         | 定义方式            | 第一个参数 | 访问实例  | 访问类    | 调用方式            |
# +--------------+---------------------+-----------+-----------+-----------+---------------------+
# | 实例方法     | def m(self)         | self      | 能        | 能(经self)| obj.m() / Cls.m(obj)|
# | 类方法       | @classmethod        | cls       | 不能      | 能        | Cls.m() / obj.m()   |
# |              | def m(cls)          |           |           |           |                     |
# | 静态方法     | @staticmethod       | 无        | 不能      | 不能      | Cls.m() / obj.m()   |
# |              | def m()             |           |           |           |                     |
# +--------------+---------------------+-----------+-----------+-----------+---------------------+
# Java 对应：实例方法 → 普通方法；类方法 → static 工厂方法（但 cls 带到子类，Java 做不到）；
#            静态方法 → static 方法（一模一样）


class User:
    """用户类：一个类里同时放三种方法"""

    platform = "demo-platform"          # 类属性（≈ Java static field）

    # Java: public User(String name, int age) { this.name = name; }
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def __repr__(self) -> str:
        return f"User(name={self.name}, age={self.age})"

    # ---------- 1. 实例方法 ----------
    # Java: public String greet() { return "我是 " + this.name; }
    def greet(self) -> str:
        """第一个参数 self = Java 的 this，只能通过实例调用才有意义"""
        return f"我是 {self.name}"

    # ---------- 2. 类方法 ----------
    # Java: public static User fromDict(Map<String,Object> d) { ... }
    # 但 Java 的 static 方法里写死类名，无法感知子类；cls 可以
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """替代构造器（工厂方法）：从 dict 造对象"""
        return cls(data["name"], data["age"])

    @classmethod
    def from_json(cls, text: str) -> "User":
        """替代构造器（工厂方法）：从 JSON 造对象"""
        return cls.from_dict(json.loads(text))

    @classmethod
    def platform_name(cls) -> str:
        """类方法访问类属性：cls.platform 而不是 User.platform"""
        return cls.platform

    # ---------- 3. 静态方法 ----------
    # Java: public static boolean isAdult(int age) { return age >= 18; }
    @staticmethod
    def is_adult(age: int) -> bool:
        """纯工具函数：不需要 self，也不需要 cls，只是恰好放在这个类里"""
        return age >= 18


# === 实例方法：实例调用 / 类调用 ===
# Java: User u = new User("张三", 20); u.greet();
u = User("张三", 20)
print(u.greet())                    # 我是 张三
# 通过类调用实例方法必须手动传 self（Java 里编译不过，Python 只是语法糖不同）
print(User.greet(u))                # 我是 张三

# === 类方法：既能类调用，也能实例调用 ===
# Java: User.fromDict(map)
print(User.from_dict({"name": "李四", "age": 17}))          # User(name=李四, age=17)
print(User.from_json('{"name": "王五", "age": 30}'))        # User(name=王五, age=30)
print(u.from_dict({"name": "李四", "age": 17}))             # User(name=李四, age=17)
print(User.platform_name())                                 # demo-platform

# === 静态方法：类调用、实例调用都可以 ===
print(User.is_adult(20))            # True
print(u.is_adult(20))               # True
print(User.is_adult(15))            # False

# === cls 的多态：类方法在子类上返回子类实例（Java static 做不到）===
class VipUser(User):
    """VIP 用户：level 有默认值，才能被 from_dict 直接构造"""

    def __init__(self, name: str, age: int, level: int = 1):
        super().__init__(name, age)     # Java: super(name, age)
        self.level = level

    def __repr__(self) -> str:
        return f"VipUser(name={self.name}, age={self.age}, level={self.level})"

vip = VipUser.from_dict({"name": "赵六", "age": 40})
print(vip)                          # VipUser(name=赵六, age=40, level=1)
# cls 是运行时收到的那个类，所以这里拿到的是 VipUser 而不是 User
print(type(vip).__name__)           # VipUser
print(isinstance(vip, User))        # True


# ==================== 二、类属性 vs 实例属性（陷阱）====================

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: 类属性 = static 字段（全类共享一份）
# Python 的坑：类属性是所有实例共享的，但「赋值」会在实例上新建一份


class Counter:
    """计数器：演示类属性与实例属性的查找规则"""

    count = 0                       # 类属性（≈ Java static int count = 0）
    tags = []                       # 可变类属性 —— 大坑，见下面

    def __init__(self, name: str):
        self.name = name            # 实例属性

    def wrong_add(self):
        # ❌ 陷阱：self.count += 1 等价于 self.count = self.count + 1
        # 读 self.count 时读到类属性 0，但「赋值」这个动作在实例上创建了新属性
        self.count += 1

    def right_add(self):
        # ✅ 正确：显式写类名（或用 type(self) 以支持子类）
        Counter.count += 1


c1 = Counter("c1")
c2 = Counter("c2")

c1.wrong_add()
c1.wrong_add()
print(Counter.count)                # 0  ← 类属性根本没变
print(c1.count)                     # 2  ← 这是 c1 自己的实例属性
print(c2.count)                     # 0  ← c2 没赋值，读到的是类属性
# 证明 c1 的实例字典里真的多了一份 count
print(c1.__dict__)                  # {'name': 'c1', 'count': 2}
print(c2.__dict__)                  # {'name': 'c2'}

c1.right_add()
print(Counter.count)                # 1  ← 这次改的是类属性
print(c2.count)                     # 1  ← c2 跟着变（共享）

# === 可变类属性被所有实例共享的坑 ===
c1.tags.append("c1加的")
print(Counter.tags)                 # ['c1加的']  ← 类属性被改了
print(c2.tags)                      # ['c1加的']  ← c2 也“被改了”，因为压根是同一个 list

# 但只要一赋值，就变成实例属性，与类属性彻底分家
c1.tags = ["c1自己的"]
print(c1.tags)                      # ['c1自己的']
print(c2.tags)                      # ['c1加的']
print(Counter.tags)                 # ['c1加的']

# === 对比 Java ===
# Java: static List<String> tags = new ArrayList<>();  // 所有实例共享同一个 list
#       tags.add(...)  →  所有实例都看得到（坑一模一样）
#       this.tags = new ArrayList<>() →  只是改了这个对象的字段引用，类字段不变
# 结论：可变类属性在 Java / Python 里都是坑，Python 没有 static 关键字，更容易踩。


# ==================== 三、__slots__ ====================

# ⭐⭐ 常用 —— 经常用
# Java: 字段必须在类里声明，写错字段名编译期就报错
# Python: 默认每个实例都有一个 __dict__，可以随时加属性（灵活但费内存、易拼错）


class SlotPoint:
    """用 __slots__ 限定属性：只有 x / y 两个槽位"""

    __slots__ = ("x", "y")          # 注意：是元组，不是 list（可以是任意可迭代，但习惯用元组）

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"SlotPoint({self.x}, {self.y})"


class DictPoint:
    """普通类：每个实例带一个 __dict__"""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"DictPoint({self.x}, {self.y})"


sp = SlotPoint(1, 2)
dp = DictPoint(1, 2)
print(sp)                           # SlotPoint(1, 2)
print(dp)                           # DictPoint(1, 2)

# === 效果1：拼错属性名立刻报错，而不是静默创建新属性 ===
try:
    sp.z = 3                        # 手滑打错
except AttributeError as e:
    # Python 3.13 的报错信息更贴心，会顺带告诉你「也没有 __dict__ 可以挂新属性」
    print(f"AttributeError: {e}")
    # 输出：AttributeError: 'SlotPoint' object has no attribute 'z' and no __dict__ for setting new attributes

dp.z = 3                            # 普通类不会报错，静默多了一个属性（bug 藏得很深）
print(dp.z)                         # 3

# === 效果2：没有 __dict__，省内存 ===
print(hasattr(sp, "__dict__"))      # False
print(hasattr(dp, "__dict__"))      # True
print(sys.getsizeof(sp))            # 48   ← __slots__ 实例的本体大小
print(sys.getsizeof(dp))            # 48   ← 普通实例的本体大小（两者本体一样）
print(sys.getsizeof(dp.__dict__))   # 296  ← 普通类每个实例额外背着的字典，差距全在这里

# === 效果3：与继承配合 —— 子类也必须定义 __slots__，否则子类又有 __dict__ ===
class SlotPoint3D(SlotPoint):
    __slots__ = ("z",)              # 子类只声明自己新增的槽位，父类的槽位自动继承

    def __init__(self, x: int, y: int, z: int):
        super().__init__(x, y)
        self.z = z

    def __repr__(self) -> str:
        return f"SlotPoint3D({self.x}, {self.y}, {self.z})"


class SlotPointNoSlot(SlotPoint):
    """没写 __slots__ 的子类：立刻被打回原形，又有 __dict__ 了"""
    pass


print(SlotPoint3D(1, 2, 3))                     # SlotPoint3D(1, 2, 3)
print(hasattr(SlotPoint3D(1, 2, 3), "__dict__"))    # False
print(hasattr(SlotPointNoSlot(1, 2), "__dict__"))   # True

# === 使用建议（重要）===
# 1. 只在「需要创建几十万+ 个实例」时才用，普通业务类不要用（会挡住动态加属性的能力）
# 2. 用了 __slots__ 就不能再给实例挂临时属性，很多框架（如 ORM 动态注入）会依赖 __dict__
# 3. __slots__ 只是省内存，不是访问控制；Python 依然没有 private


# ==================== 四、多继承与 MRO ====================

# ⭐⭐ 常用 —— 经常用
# Java: 只能单继承类 + 多实现接口（Java 8+ 接口可以有 default 方法）
# Python: 直接多继承，靠 C3 线性化算出唯一的方法查找顺序 = MRO


class A:
    def hello(self):
        print("A.hello")


class B(A):
    def hello(self):
        print("B.hello")
        super().hello()             # 沿 MRO 找「B 之后」的下一个，不一定是 A


class C(A):
    def hello(self):
        print("C.hello")
        super().hello()


class D(B, C):
    """菱形继承：D → B → C → A → object"""

    def hello(self):
        print("D.hello")
        super().hello()


# === 查看 MRO（方法解析顺序）===
# Java 没有这个概念，Java 用「类优先于接口、冲突必须显式重写」来规避
print([c.__name__ for c in D.__mro__])      # ['D', 'B', 'C', 'A', 'object']
print(D.__mro__[1])                         # <class '__main__.B'>

# === 菱形继承的调用链：A 只被调用一次 ===
D().hello()
# 输出：
# D.hello
# B.hello
# C.hello
# A.hello

# 为什么 A 只出现一次？因为 MRO 是一条线：D → B → C → A → object，
# super() 的语义是「在这条线上继续往后走」，A 排在 C 后面，走完 C 才轮到 A，且只走一次。
# 如果 super() 是「调用父类」，那 B 调 A、C 又调 A，A 就会被执行两次。

# === 铁证：super() 不是「调用父类」===
class X:
    def tag(self):
        return "X"


class Y(X):
    def tag(self):
        return "Y"


class Z(X):
    def tag(self):
        return "Z"


class W(Y, Z):
    pass


print([c.__name__ for c in W.__mro__])      # ['W', 'Y', 'Z', 'X', 'object']
# super(Y, W()).tag() 的含义：在 W 的 MRO 里，从 Y 的「下一个」开始找 tag
# Y 的父类明明是 X，但按 MRO 下一个是 Z，所以结果是 Z —— super() 看的是 MRO，不是继承声明
print(super(Y, W()).tag())                  # Z

# === 对比 Java ===
# Java: class D extends B implements C  → 只有一条父类链，默认方法冲突必须在 D 里显式重写
# Python: C3 线性化自动算出顺序，super() 沿链传递，天然解决菱形问题
# 记住一句话：super() = 「沿 MRO 找下一个」，不是「调用父类」。


# ==================== 五、Mixin 模式 ====================

# ⭐⭐ 常用 —— 经常用
# Java: 用 interface + default 方法，或组合 + 委托 来复用横切能力
# Python: 用「不含状态的小类 + 多继承」直接把能力混入（Mixin）
# 约定：1) 类名必须以 Mixin 结尾  2) Mixin 不单独实例化  3) Mixin 通常不定义 __init__


class SerializableMixin:
    """能力：把对象转成 dict。依赖宿主类有 __dict__"""

    def to_dict(self) -> dict:
        return dict(self.__dict__)


class JsonMixin:
    """能力：把对象转成 JSON。依赖宿主类实现了 to_dict"""

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class Product(SerializableMixin, JsonMixin):
    """业务类：Mixin 写在前面，业务基类写在最后（重要习惯）"""

    def __init__(self, sku: str, price: float):
        self.sku = sku
        self.price = price

    def __repr__(self) -> str:
        return f"Product(sku={self.sku}, price={self.price})"


p = Product("A-001", 99.5)
print(p)                                    # Product(sku=A-001, price=99.5)
print(p.to_dict())                          # {'sku': 'A-001', 'price': 99.5}
print(p.to_json())                          # {"sku": "A-001", "price": 99.5}
print([c.__name__ for c in Product.__mro__])    # ['Product', 'SerializableMixin', 'JsonMixin', 'object']

# Mixin 是被「混入」的，单独实例化没有意义（没有业务数据，方法也没法用）
# SerializableMixin()  →  to_dict() 只会返回 {}

# === Java 对照写法 ===
# public interface Serializable { default Map<String,Object> toDict() {...} }
# public class Product implements Serializable, Jsonable { ... }
# 区别：Java 接口的 default 方法不能访问实现类的字段（只能靠 getter）；
#       Python Mixin 直接 self.__dict__ 就能拿到全部字段，所以 Mixin 更强也更容易被滥用。


# ==================== 六、魔法方法补全 ====================

# ⭐⭐ 常用 —— 经常用
# 第7课讲过 __init__ / __str__ / __repr__ / __eq__ / __add__，这里补齐剩下的常用魔法方法。
# 核心思想：Python 的语法（len()、[]、in、for、()）都会被翻译成对魔法方法的调用。


# ---------- 6.1 __len__：让 len() 可用 ----------
# Java: size() / length() 是普通方法，语法层面没有统一协议
class Basket:
    def __init__(self, items):
        self.items = list(items)

    def __len__(self) -> int:
        return len(self.items)


# 注意：__len__ 必须返回非负整数，返回别的类型会直接 TypeError
print(len(Basket(["苹果", "香蕉"])))         # 2


# ---------- 6.2 __getitem__ / __setitem__ / __delitem__：下标操作 ----------
# Java: get(i) / set(i, v) / remove(i)，必须显式调方法
# 额外福利：只实现 __getitem__ 就能让对象「可迭代」，也能用 in（旧式迭代协议）

class OnlyGetItem:
    """只实现 __getitem__，却同时获得了 for 和 in 的能力"""

    def __getitem__(self, index):
        if index >= 3:
            raise IndexError(index)     # 迭代协议靠 IndexError 判断结束
        return index * 10


print([x for x in OnlyGetItem()])           # [0, 10, 20]
print(0 in OnlyGetItem())                   # True   ← 没有 __contains__ 时靠 __getitem__ 迭代
print(5 in OnlyGetItem())                   # False


# ---------- 6.3 自定义容器：把魔法方法串起来 ----------
class Playlist:
    """自定义容器类：len / 下标 / in / for / 调用 全部支持"""

    def __init__(self, name: str, songs=None):
        self.name = name
        self._songs = list(songs) if songs else []

    def __repr__(self) -> str:
        return f"Playlist(name={self.name}, songs={self._songs})"

    # Java: public int size()
    def __len__(self) -> int:
        return len(self._songs)

    # Java: public String get(int i)
    def __getitem__(self, index):
        # 关键：这里原样透传给 list，所以切片 pl[0:2] 自动也能用（切片传进来的是 slice 对象）
        return self._songs[index]

    # Java: public void set(int i, String v)
    def __setitem__(self, index, value):
        self._songs[index] = value

    # Java: public void remove(int i)
    def __delitem__(self, index):
        del self._songs[index]

    # Java: public boolean contains(String s)
    # 不实现 __contains__ 也能用 in，但会退化成遍历比较，性能差；显式实现更高效
    def __contains__(self, item) -> bool:
        return item in self._songs

    # Java: public Iterator<String> iterator()
    def __iter__(self):
        # 直接返回内置 list 的迭代器，是最省事的写法；要自定义逻辑就写 __next__（见 6.4）
        return iter(self._songs)

    # Java: 无对应物 —— 让实例像函数一样被调用
    def __call__(self, times: int = 1) -> str:
        return " ".join(self._songs * times)


pl = Playlist("通勤歌单", ["A", "B", "C"])
print(len(pl))                      # 3
print(pl[0])                        # A
print(pl[-1])                       # C
print(pl[0:2])                      # ['A', 'B']
pl[0] = "AA"                        # 触发 __setitem__
print(pl)                           # Playlist(name=通勤歌单, songs=['AA', 'B', 'C'])
del pl[2]                           # 触发 __delitem__
print(pl)                           # Playlist(name=通勤歌单, songs=['AA', 'B'])
print("B" in pl)                    # True
print("Z" in pl)                    # False
for song in pl:                     # 触发 __iter__
    print(song)
# 输出：
# AA
# B
print(pl(2))                        # AA B AA B


# ---------- 6.4 __iter__ / __next__：自己当迭代器 ----------
# Java: implements Iterator<T>，手工维护游标 + hasNext()/next()
class Countdown:
    """倒计时迭代器：自己既是可迭代对象，也是迭代器"""

    def __init__(self, start: int):
        self.current = start

    def __iter__(self):
        return self                     # 自己就是迭代器，返回自己

    def __next__(self):
        if self.current <= 0:
            raise StopIteration         # Java: hasNext() 返回 false 的等价物，必须抛
        self.current -= 1
        return self.current + 1


for n in Countdown(3):
    print(n, end=" ")                   # 3 2 1
print()

# 手动 next() 也一样
cd = Countdown(2)
print(next(cd))                         # 2
print(next(cd))                         # 1
# next(cd) 再来一次就会抛 StopIteration（for 会自动捕获它来结束循环）


# ---------- 6.5 __call__：让实例像函数一样调用 ----------
# Java: 需要实现 java.util.function.Function / Callable 接口
# Python: 只要实现 __call__，对象就能“带括号调用”，常用于「带状态的函数」
class Adder:
    def __init__(self, base: int):
        self.base = base

    def __call__(self, x: int) -> int:
        return self.base + x


add5 = Adder(5)
print(add5(3))                          # 8
print(callable(add5))                   # True
print(callable(Adder))                  # True  ← 类本身也可调用（调它就是构造实例）


# ---------- 6.6 __hash__：可哈希，能当 dict 的 key ----------
# Java: 重写 equals() 必须同时重写 hashCode()，规则完全一致
class UserId:
    def __init__(self, value: int):
        self.value = value

    def __repr__(self) -> str:
        return f"UserId({self.value})"

    def __eq__(self, other) -> bool:
        return isinstance(other, UserId) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


user_map = {UserId(1): "张三", UserId(2): "李四"}
print(user_map[UserId(1)])              # 张三   ← 用「等值的新对象」也能查到
print(UserId(1) == UserId(1))           # True

# ⚠️ 致命联动：类里一旦定义了 __eq__ 而没定义 __hash__，
# Python 会自动把 __hash__ 置为 None，对象立刻变成不可哈希 → 不能放进 set / 不能当 dict key
class NoHash:
    def __eq__(self, other) -> bool:
        return True


print(NoHash.__hash__)                  # None
try:
    {NoHash()}                          # 想放进 set
except TypeError as e:
    print(f"TypeError: {e}")            # TypeError: unhashable type: 'NoHash'

# 结论：可变对象用 __eq__ 不实现 __hash__（本来就该不可哈希）；
#       不可变值对象要把两个都实现，且 __hash__ 必须只依赖参与 __eq__ 比较的字段。


# ---------- 6.7 __bool__：真值判断 ----------
# Java: 没有这套机制，if 只认 boolean 表达式，不存在「对象自己决定真假」
class Cart:
    def __init__(self, items):
        self.items = list(items)

    def __len__(self) -> int:
        return len(self.items)

    def __bool__(self) -> bool:
        # 业务规则：只有「有效商品」才算非空
        return any(item != "无效" for item in self.items)


print(bool(Cart([])))                   # False  ← any([]) 是 False
print(bool(Cart(["无效"])))             # False
print(bool(Cart(["苹果"])))             # True
print(len(Cart(["无效"])))              # 1      ← __len__ 依然说长度是 1，两者互不干扰

# 没定义 __bool__ 和 __len__ 的对象，真值恒为 True（哪怕它看起来「是空的」）
class Empty:
    pass


print(bool(Empty()))                    # True
# 查找顺序：__bool__ → 没有就找 __len__ → 都没有就默认 True
# 所以 Basket（只定义了 __len__）的真值是：len 为 0 就是 False
print(bool(Basket([])))                 # False
print(bool(Basket(["苹果"])))           # True


# ---------- 6.8 比较方法 + @functools.total_ordering ----------
# Java: Comparable<T> 的 compareTo() 一个方法搞定所有比较
# Python: 要想支持 < > <= >= 得实现 4 个方法，太啰嗦 → 用 total_ordering 自动补齐
@functools.total_ordering
class Version:
    """语义化版本号：只实现 __eq__ 和 __lt__，其余比较由装饰器自动生成"""

    def __init__(self, major: int, minor: int):
        self.major = major
        self.minor = minor

    def __repr__(self) -> str:
        return f"Version({self.major}.{self.minor})"

    def _key(self):
        return (self.major, self.minor)

    def __eq__(self, other) -> bool:
        return isinstance(other, Version) and self._key() == other._key()

    def __lt__(self, other) -> bool:
        return self._key() < other._key()

    # 注意：total_ordering 只补方法，不会替你实现 __hash__，需要自己加（见 6.6）


print(Version(1, 2) < Version(1, 10))   # True   ← 元组比较按元素逐个比，2 < 10
print(Version(2, 0) > Version(1, 10))   # True   ← 这个方法不是手写的，是装饰器生成的
print(Version(1, 2) <= Version(1, 2))   # True
print(Version(1, 2) >= Version(1, 2))   # True
print(sorted([Version(2, 0), Version(1, 10), Version(1, 2)]))
# 输出：[Version(1.2), Version(1.10), Version(2.0)]


# ==================== 七、__new__ vs __init__ ====================

# ⭐ 了解 —— 用到再查
# Java: 对象的创建只有一个 new，构造器里同时干「分配」和「初始化」两件事
# Python 拆成两步：
#   __new__(cls, ...)  → 负责「创建」并返回一个实例（真正的构造器）
#   __init__(self, ...) → 负责「初始化」刚创建出来的实例，返回值必须是 None
# 流程：先调用 __new__ 拿到对象，如果它是 cls 的实例，再自动调用 __init__

class Order:
    def __new__(cls, *args, **kwargs):
        print("1. __new__ 负责创建对象")
        # object.__new__(cls) 才是真正分配内存的那一步
        return super().__new__(cls)

    def __init__(self, order_no: str):
        print("2. __init__ 负责初始化对象")
        self.order_no = order_no


o = Order("SO-001")
# 输出：
# 1. __new__ 负责创建对象
# 2. __init__ 负责初始化对象
print(o.order_no)                   # SO-001


# === 场景1：不可变类型的子类化（必须用 __new__）===
# 因为 str / int / tuple 不可变，值在「创建时」就定死了，__init__ 里改不了
class UpperStr(str):
    def __new__(cls, value: str):
        return super().__new__(cls, value.upper())   # 在创建时就把值变成大写

    # 父类有 __init__，这里可以完全不管


print(UpperStr("abc"))              # ABC


# === 场景2：单例（本课示例，生产环境请用模块级变量或依赖注入）===
class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance                 # 永远返回同一个对象

    def __init__(self, name: str = "default"):
        self.name = name


s1 = Singleton("A")
s2 = Singleton("B")
print(s1 is s2)                     # True
# ⚠️ 注意：__init__ 每次都会在新返回的那个对象上重新执行，
# 所以第二次构造会把 name 覆盖成 "B"
print(s1.name)                      # B
print(s2.name)                      # B


# ==================== 八、鸭子类型 vs 接口 ====================

# ⭐⭐ 常用 —— 经常用
# Java: 强约束 —— 必须 implements 接口，编译器检查；类型不对编译不过
# Python: 只看「有没有这个方法」，不关心继承关系，运行时才报错

class Dog:
    def speak(self) -> str:
        return "汪汪"


class Cat:
    def speak(self) -> str:
        return "喵"


class Robot:
    """没有继承任何基类，但只要它有 speak，就能被同一段代码使用"""

    def speak(self) -> str:
        return "哔哔"


def make_speak(thing):
    """Java: void makeSpeak(Speaker thing)  —— 参数类型被接口锁死"""
    return thing.speak()


for animal in (Dog(), Cat(), Robot()):
    print(make_speak(animal))
# 输出：
# 汪汪
# 喵
# 哔哔

# === 鸭子类型的代价：传错对象要到运行时才炸 ===
class Stone:
    pass


try:
    make_speak(Stone())
except AttributeError as e:
    print(f"AttributeError: {e}")
    # AttributeError: 'Stone' object has no attribute 'speak'

# === EAFP 风格：先干，出错再处理（Python 哲学）===
# Java 习惯 LBYL（Look Before You Leap）：先检查类型再调用
def safe_speak(thing) -> str:
    try:
        return thing.speak()
    except AttributeError:
        return "这个东西不会说话"


print(safe_speak(Robot()))          # 哔哔
print(safe_speak(Stone()))          # 这个东西不会说话

# === 想要 Java 那样的静态约束：用 Protocol（结构化子类型）===
# Java: public interface Speaker { String speak(); }  +  implements Speaker
# Python: Protocol 描述「长什么样就算」，不需要 implements，靠类型检查器（mypy）静态校验
# 详见第18课
from typing import Protocol


class Speaker(Protocol):
    """只要实现了 speak() -> str，就「符合」Speaker，无需显式继承"""

    def speak(self) -> str: ...


def make_speak_typed(thing: Speaker) -> str:
    """类型提示：这里只接受符合 Speaker 的对象（运行时不做检查，mypy 会检查）"""
    return thing.speak()


print(make_speak_typed(Dog()))      # 汪汪


# ==================== 总结对比 ====================
# Java                              → Python
# static 方法                        → @staticmethod（完全等价）
# static 工厂方法                    → @classmethod（多一个 cls，支持子类多态）
# static 字段                        → 类属性（但 Python 有 self.x += 1 的陷阱）
# 字段必须声明                       → 默认自由加属性，需要限制就用 __slots__
# 单继承 + 多接口                    → 多继承 + C3 线性化（MRO）
# 接口 default 方法复用              → Mixin 模式
# equals() + hashCode()              → __eq__ + __hash__（必须成对）
# Comparable.compareTo()             → __lt__ + @functools.total_ordering
# Iterator / Iterable                → __iter__ / __next__
# Callable / Function                → __call__
# 无                                 → __len__ / __getitem__ / __contains__ / __bool__
# 构造器 new                         → __new__（创建）+ __init__（初始化）
# implements Interface               → duck typing，或 typing.Protocol（静态检查）

print("=== 16 面向对象进阶 结束 ===")
