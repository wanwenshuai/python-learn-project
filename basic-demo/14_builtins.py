"""
===== 第14课：内置函数与 collections =====
对标 Java 的 Collections 工具类 / Guava
"""

# ==================== 一、迭代与排序类内置函数 ====================

# -------------------- zip 配对迭代 --------------------
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: 没有内置，要自己写 for (int i = 0; i < a.size(); i++)，或用 IntStream.range
names = ["Alice", "Bob", "Carol"]
scores = [90, 85, 95]

# Java: for (int i = 0; i < Math.min(names.size(), scores.size()); i++)
pairs = list(zip(names, scores))
print(pairs)                       # [('Alice', 90), ('Bob', 85), ('Carol', 95)]

# 直接解包遍历（最常用）
for name, score in zip(names, scores):
    print(f"{name}={score}", end=" ")
print()                            # Alice=90 Bob=85 Carol=95

# ⚠️ 和 Java 不同：zip 以最短的序列为准，多出来的直接丢弃，不报错
print(list(zip([1, 2, 3], ["a", "b"])))   # [(1, 'a'), (2, 'b')]

# Python 3.10+ 可用 strict=True 强制长度一致（不等就抛 ValueError）
# print(list(zip([1, 2, 3], ["a", "b"], strict=True)))   # ValueError

# zip 返回的是迭代器（惰性），不是列表
z = zip(names, scores)
print(type(z))                     # <class 'zip'>

# -------------------- zip(*matrix) 转置矩阵 --------------------
# ⭐⭐⭐ 必会 —— 一行代码搞定转置
# Java: 需要双重 for 循环手动赋值到新数组，或引入第三方库
matrix = [[1, 2, 3],
          [4, 5, 6]]

# * 号把 matrix 拆成 (row1, row2) 两个参数传给 zip
transposed = list(zip(*matrix))
print(transposed)                  # [(1, 4), (2, 5), (3, 6)]

# 想要列表套列表（而非元组）
transposed_list = [list(row) for row in zip(*matrix)]
print(transposed_list)             # [[1, 4], [2, 5], [3, 6]]

# -------------------- zip 配合 dict() 建字典 --------------------
# ⭐⭐⭐ 必会
# Java: 需要 Map<String, Integer> map = new HashMap<>(); 再循环 put
keys = ["name", "age", "city"]
values = ["Tom", 25, "Beijing"]

user = dict(zip(keys, values))
print(user)                        # {'name': 'Tom', 'age': 25, 'city': 'Beijing'}

# 反向操作：字典拆成两个序列
print(list(user.keys()))           # ['name', 'age', 'city']
print(list(user.values()))         # ['Tom', 25, 'Beijing']

# -------------------- sorted(key=, reverse=) --------------------
# ⭐⭐⭐ 必会
# Java: list.stream().sorted(Comparator.comparing(...)).collect(...) —— 会返回新集合
# Python: sorted() 返回新列表，list.sort() 原地排序（返回 None）
nums = [3, 1, 4, 1, 5, 9, 2, 6]
print(sorted(nums))                # [1, 1, 2, 3, 4, 5, 6, 9]
print(sorted(nums, reverse=True))  # [9, 6, 5, 4, 3, 2, 1, 1]
print(nums)                        # [3, 1, 4, 1, 5, 9, 2, 6] ← 原列表不变

words = ["banana", "apple", "cherry"]
print(sorted(words, key=len))      # ['apple', 'banana', 'cherry']

# Java: Comparator.comparing(Person::getAge).reversed()
print(sorted(words, key=len, reverse=True))   # ['banana', 'cherry', 'apple']

# -------------------- 多级排序 key 返回元组 --------------------
# ⭐⭐⭐ 必会 —— Java 里要写 Comparator.thenComparing()，Python 直接返回元组
# Java: Comparator.comparing(Student::getGrade).thenComparing(Student::getAge)
students = [
    ("Tom", 90, 20),
    ("Amy", 90, 18),
    ("Bob", 85, 22),
    ("Dan", 90, 18),
]

# 先按成绩降序，成绩相同再按年龄升序
# 技巧：降序用 -x，升序用 x（前提是数值类型）
result = sorted(students, key=lambda s: (-s[1], s[2]))
print(result)   # [('Amy', 90, 18), ('Dan', 90, 18), ('Tom', 90, 20), ('Bob', 85, 22)]

# ⭐⭐ 常用 —— 字符串没法取负，需要多趟排序（Python 排序稳定）
# 先按次要字段升序排，再按主要字段降序排，稳定性保证结果正确
result2 = sorted(students, key=lambda s: s[2])            # 先按年龄升序
result2.sort(key=lambda s: s[1], reverse=True)            # 再按成绩降序
print(result2)  # [('Amy', 90, 18), ('Dan', 90, 18), ('Tom', 90, 20), ('Bob', 85, 22)]

# -------------------- operator.itemgetter / attrgetter --------------------
# ⭐⭐ 常用 —— 比 lambda 快，且可读性好
# Java: Comparator.comparing(Student::getAge) 的方法引用
import operator

# itemgetter 取下标（dict 也能用，取的是 key）
get_score = operator.itemgetter(1)
print(get_score(("Tom", 90, 20)))       # 90

print(sorted(students, key=operator.itemgetter(1)))
# [('Bob', 85, 22), ('Tom', 90, 20), ('Amy', 90, 18), ('Dan', 90, 18)]

# 多个 itemgetter 也可以直接当排序 key（返回元组）
print(sorted(students, key=operator.itemgetter(1, 2)))
# [('Bob', 85, 22), ('Amy', 90, 18), ('Dan', 90, 18), ('Tom', 90, 20)]

# 对字典列表排序（后端接口最常见场景）
rows = [{"id": 3, "name": "c"}, {"id": 1, "name": "a"}, {"id": 2, "name": "b"}]
print(sorted(rows, key=operator.itemgetter("id")))
# [{'id': 1, 'name': 'a'}, {'id': 2, 'name': 'b'}, {'id': 3, 'name': 'c'}]


# attrgetter 取属性
# Java: Comparator.comparing(Student::getAge)
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __repr__(self):
        return f"Student({self.name}, {self.age})"


stu_list = [Student("Tom", 20), Student("Amy", 18), Student("Bob", 22)]
print(sorted(stu_list, key=operator.attrgetter("age")))
# [Student(Amy, 18), Student(Tom, 20), Student(Bob, 22)]

# -------------------- min / max(key=) --------------------
# ⭐⭐⭐ 必会
# Java: stream().min(Comparator.comparing(...)).get()
print(max([3, 1, 4, 1, 5]))                  # 5
print(min([3, 1, 4, 1, 5]))                  # 1
print(max(words, key=len))                   # banana
print(min(students, key=operator.itemgetter(1)))   # ('Bob', 85, 22)

# ⚠️ 空序列会抛 ValueError，Java 的 Optional 不会
# print(max([]))                             # ValueError: max() arg is an empty sequence

# Python 3.4+ 支持 default，空序列返回默认值
print(max([], default=0))                    # 0

# 同时拿到最大值的下标（Java 里没有直接对应）
print(max(range(len(nums)), key=nums.__getitem__))   # 5

# -------------------- enumerate(start=) --------------------
# ⭐⭐⭐ 必会
# Java: for (int i = 0; i < list.size(); i++) 自己维护下标
fruits = ["apple", "banana", "cherry"]

for i, fruit in enumerate(fruits):
    print(i, fruit, end=" | ")
print()                                      # 0 apple | 1 banana | 2 cherry |

# start 参数（Java 里需要 i+1）
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}.{fruit}", end=" ")
print()                                      # 1.apple 2.banana 3.cherry

# 常用：转成字典
print(dict(enumerate(fruits)))               # {0: 'apple', 1: 'banana', 2: 'cherry'}

# -------------------- reversed --------------------
# ⭐⭐ 常用
# Java: Collections.reverse(list) —— 原地修改；或 new StringBuilder(s).reverse()
print(list(reversed([1, 2, 3])))             # [3, 2, 1]
print(list(reversed("abc")))                 # ['c', 'b', 'a']

# reversed 返回迭代器，不占额外内存（对比 nums[::-1] 会复制一份）
print(list(reversed(range(5))))              # [4, 3, 2, 1, 0]

# ⚠️ reversed 只支持序列或实现了 __reversed__ 的对象，不支持 set/dict
# print(list(reversed({1, 2, 3})))           # TypeError

# -------------------- any / all --------------------
# ⭐⭐⭐ 必会
# Java: stream().anyMatch(...) / allMatch(...)
checks = [True, True, False]
print(any(checks))                           # True   有任意一个为真
print(all(checks))                           # False  全部为真才为真

print(any([0, "", None]))                    # False  空值都是假
print(all([1, "a", [1]]))                    # True

# 典型用法：校验
ages = [20, 25, 30]
print(all(age >= 18 for age in ages))        # True

# ⚠️ 短路求值，和 Java Stream 一样；空序列 any=False、all=True（数学上的约定）
print(any([]))                               # False
print(all([]))                               # True

# ==================== 二、数值类 ====================

# -------------------- sum(start=) --------------------
# ⭐⭐⭐ 必会
# Java: stream().mapToInt(Integer::intValue).sum()，没起始值参数
print(sum([1, 2, 3, 4]))                     # 10
print(sum([1, 2, 3, 4], 100))                # 110  第二个参数是起始值
print(sum(range(101)))                       # 5050
print(sum([[1, 2], [3, 4]], []))             # [1, 2, 3, 4]  ← 起始值给 [] 可拼接列表

# -------------------- abs / round / divmod --------------------
# ⭐⭐ 常用
# Java: Math.abs(-5)
print(abs(-5))                               # 5
print(abs(-3.14))                            # 3.14

# Java: Math.round(2.5) → 3（四舍五入）
# ⚠️ Python 的 round 是「银行家舍入」：.5 时向偶数靠拢
print(round(2.5))                            # 2  ← Java 是 3！
print(round(3.5))                            # 4
print(round(-2.5))                           # -2
print(round(2.675, 2))                       # 2.67 ← 浮点精度 + 银行家舍入

# divmod 同时返回商和余数（Java 没有，要算两次）
# Java: int q = 17 / 5; int r = 17 % 5;
q, r = divmod(17, 5)
print(q, r)                                  # 3 2

# 应用：秒数转时分秒
total_seconds = 3725
minutes, seconds = divmod(total_seconds, 60)
hours, minutes = divmod(minutes, 60)
print(f"{hours}:{minutes:02d}:{seconds:02d}")   # 1:02:05

# 负数取余：Python 结果符号跟除数走，Java 跟被除数走
print(-17 % 5)                               # 3   ← Java 是 -2
print(divmod(-17, 5))                        # (-4, 3)

# -------------------- pow（含三参数取模）--------------------
# ⭐⭐ 常用
# Java: Math.pow(2, 10) 返回 double
print(pow(2, 10))                            # 1024
print(2 ** 10)                               # 1024  运算符写法

# ⭐⭐⭐ 三参数版：pow(base, exp, mod) 是「快速幂取模」，Java 要 BigInteger.modPow
# Java: BigInteger.valueOf(2).modPow(BigInteger.valueOf(100), BigInteger.valueOf(1000))
print(pow(2, 100, 1000))                     # 376
print(pow(3, 1000, 7))                       # 4   ← 大数场景下毫秒级完成

# ⚠️ 三参数版要求整数；pow(2, 0.5) 可以，pow(2, 0.5, 3) 报错
print(pow(4, 0.5))                           # 2.0

# ==================== 三、类型与反射 ====================

# -------------------- type / isinstance / issubclass --------------------
# ⭐⭐ 常用
# Java: obj.getClass() / obj instanceof String
print(type(42))                              # <class 'int'>
print(type("abc") == str)                    # True

# ⚠️ 判断类型优先用 isinstance，因为它支持继承，且更符合 Python 风格
# Java: obj instanceof Number
print(isinstance(42, int))                   # True

# ⭐⭐⭐ isinstance 第二个参数可以是元组（Java 要写多个 ||）
# Java: obj instanceof String || obj instanceof Integer
print(isinstance(42, (int, float)))          # True
print(isinstance(42, (str, list)))           # False

# ⚠️ Python 的 bool 是 int 的子类，这点和 Java 完全不同
print(isinstance(True, int))                 # True
print(True + True)                           # 2

# issubclass 判断类之间的继承关系
# Java: Number.class.isAssignableFrom(Integer.class)
print(issubclass(bool, int))                 # True
print(issubclass(int, bool))                 # False

# -------------------- callable --------------------
# ⭐⭐ 常用
# Java: obj instanceof Function / 接口类型判断
# Python 里「可调用」是统一协议：函数、lambda、类、实现了 __call__ 的实例都可调用
print(callable(len))                         # True
print(callable(lambda x: x))                 # True
print(callable(Student))                     # True  ← 类本身可调用（构造实例）
print(callable("abc"))                       # False


class Adder:
    def __call__(self, a, b):
        return a + b


add_obj = Adder()
print(callable(add_obj))                     # True
print(add_obj(1, 2))                         # 3

# -------------------- getattr / setattr / hasattr / delattr --------------------
# ⭐⭐ 常用 —— 对标 Java 反射
# Java: clazz.getDeclaredField("name"); field.setAccessible(true); field.get(obj)
# Python 没有 private 强制约束，属性访问天生开放，不需要 setAccessible
person = Student("Tom", 20)

# Java: person.getClass().getField("name").get(person)
print(getattr(person, "name"))               # Tom

# 等价于点号访问
print(getattr(person, "name") == person.name)   # True

# 第三个参数是默认值：属性不存在时返回它，而不是抛异常
# Java: 需要 try/catch NoSuchFieldException
print(getattr(person, "email", "未设置"))     # 未设置

# hasattr 等价于 try: getattr / except AttributeError
# Java: clazz.getDeclaredFields() 再遍历比对
print(hasattr(person, "age"))                # True
print(hasattr(person, "email"))              # False

# setattr 动态设置属性（Java 反射做不到这么轻松）
# Java: field.setAccessible(true); field.set(person, 30);
setattr(person, "age", 30)
print(person.age)                            # 30

# 甚至能凭空加属性（Java 完全不行，字段必须编译期声明）
setattr(person, "email", "tom@example.com")
print(person.email)                          # tom@example.com

# delattr 删除属性
delattr(person, "email")
print(hasattr(person, "email"))              # False

# ⭐⭐⭐ 典型应用：把 dict 批量转成对象属性（后端接收 JSON 常用）
data = {"name": "Amy", "age": 18}
obj = Student.__new__(Student)               # 不走 __init__ 创建空对象
for k, v in data.items():
    setattr(obj, k, v)
print(obj)                                   # Student(Amy, 18)

# -------------------- id / hash / repr --------------------
# ⭐ 了解 —— 用到再查
# Java: System.identityHashCode(obj) / obj.hashCode() / obj.toString()
x = [1, 2, 3]
print(id(x) > 0)                             # True  ← id 是内存地址，每次运行都不同
print(id(x) == id(x))                        # True  ← 同一对象 id 相同

# hash：可哈希才能做 dict 的 key / set 的元素
# ⚠️ 字符串的 hash 每次进程启动都不同（哈希随机化，防哈希碰撞攻击），别打印它
print(hash(42))                              # 42
print(hash((1, 2)))                          # -3550055125485641917
print(hash("abc") == hash("abc"))            # True  ← 同进程内稳定

# ⚠️ list/dict/set 是不可哈希的，所以不能当 dict 的 key
# Java 的 HashMap key 只要是 Object 都行，Python 要求可哈希
# print(hash([1, 2]))                        # TypeError: unhashable type: 'list'

# repr：给开发者看的字符串，≈ Java 的 toString()（但更强调「可重建」）
# Java: obj.toString()  /  String.valueOf()
print(repr("abc"))                           # 'abc'    ← 带引号
print(repr([1, "a"]))                        # [1, 'a']
print(str("abc"))                            # abc      ← 不带引号

# ==================== 四、编码与进制 ====================

# -------------------- ord / chr --------------------
# ⭐ 了解 —— 用到再查
# Java: (int) 'A'  /  Character.getNumericValue
print(ord("A"))                              # 65
print(ord("a"))                              # 97
print(ord("中"))                             # 20013   ← Python 直接支持 Unicode，Java 的 char 只有 16 位
print(chr(65))                               # A
print(chr(20013))                            # 中

# -------------------- bin / hex / oct --------------------
# ⭐ 了解
# Java: Integer.toBinaryString(255) / Integer.toHexString(255) / Integer.toOctalString(255)
print(bin(255))                              # 0b11111111   ← 带前缀，Java 不带
print(hex(255))                              # 0xff
print(oct(255))                              # 0o377

# 想去掉前缀
print(bin(255)[2:])                          # 11111111

# 反向：从字符串按进制解析（Java: Integer.parseInt(s, 2)）
print(int("11111111", 2))                    # 255
print(int("ff", 16))                         # 255
print(int("377", 8))                         # 255

# -------------------- format 进制与格式化 --------------------
# ⭐⭐ 常用 —— 比 Java String.format 更灵活
# Java: String.format("%02d", 5) / String.format("%,d", 1234567)
print(format(255, "b"))                      # 11111111   ← 不带前缀
print(format(255, "x"))                      # ff
print(format(255, "X"))                      # FF
print(format(255, "o"))                      # 377
print(format(255, "08b"))                    # 11111111   ← 补零到 8 位
print(format(5, "08b"))                      # 00000101

# 内置 format 的简写是 f-string / str.format 的格式说明符
print(f"{255:#x}")                           # 0xff       ← # 表示带前缀
print(f"{3.14159:.2f}")                      # 3.14
print(f"{1234567:,}")                        # 1,234,567
print(f"{0.856:.1%}")                        # 85.6%
print(f"{42:>10}|")                          #         42|
print(f"{42:<10}|")                          # 42        |
print(f"{42:^10}|")                          #     42    |

# ==================== 五、collections 模块（本课重点）====================

# -------------------- Counter：计数器 --------------------
# ⭐⭐⭐ 必会
# Java: 手写 Map<String, Integer> map = new HashMap<>();
#      map.merge(word, 1, Integer::sum);
# Python 一行搞定
from collections import Counter

words = ["apple", "banana", "apple", "cherry", "apple", "banana"]
counter = Counter(words)
print(counter)                               # Counter({'apple': 3, 'banana': 2, 'cherry': 1})

# most_common(n)：取前 n 个（Java 要 stream().sorted().limit()）
print(counter.most_common(2))                # [('apple', 3), ('banana', 2)]
print(counter.most_common())                 # [('apple', 3), ('banana', 2), ('cherry', 1)]

# 取值：不存在的 key 返回 0，不抛 KeyError（Java 的 map.get 返回 null）
print(counter["apple"])                      # 3
print(counter["nothing"])                    # 0

# update：累加计数
counter.update(["apple", "durian"])
print(counter["apple"], counter["durian"])   # 4 1

# 从字符串统计字符（经典用法）
char_count = Counter("hello")
print(char_count)                            # Counter({'l': 2, 'h': 1, 'e': 1, 'o': 1})

# elements()：按计数展开成迭代器（计数为 0 或负数的元素不输出）
c2 = Counter(a=2, b=1)
print(sorted(c2.elements()))                 # ['a', 'a', 'b']
print(list(c2.elements()))                   # ['a', 'a', 'b']

# 算术运算：Java 要自己遍历两个 Map，Python 直接 + - & |
c1 = Counter(a=3, b=1)
c3 = Counter(a=1, b=2)
print(c1 + c3)                               # Counter({'a': 4, 'b': 3})
print(c1 - c3)                               # Counter({'a': 2})  ← 只保留正数
print(c1 & c3)                               # Counter({'a': 1, 'b': 1})  ← 取小值（交集）
print(c1 | c3)                               # Counter({'a': 3, 'b': 2})  ← 取大值（并集）

# 应用：统计词频 TopN
text = "the quick brown fox jumps over the lazy dog the fox"
top2 = Counter(text.split()).most_common(2)
print(top2)                                  # [('the', 3), ('fox', 2)]

# -------------------- defaultdict：带默认值的字典 --------------------
# ⭐⭐⭐ 必会 —— 彻底消灭 KeyError
# Java: map.computeIfAbsent(key, k -> new ArrayList<>()).add(v);
from collections import defaultdict

# 用法1：defaultdict(int) 计数（比 Counter 更朴素的写法）
count = defaultdict(int)
for w in ["a", "b", "a", "c", "a"]:
    count[w] += 1                            # key 不存在时自动初始化为 0
print(dict(count))                           # {'a': 3, 'b': 1, 'c': 1}

# Java 对照：Map<String,Integer> m = new HashMap<>();
#           m.put(w, m.getOrDefault(w, 0) + 1);

# 用法2：defaultdict(list) 分组（后端最常见的「按某字段分组」）
# Java: Map<String, List<User>> groups = new HashMap<>();
#      for (User u : users) groups.computeIfAbsent(u.getCity(), k -> new ArrayList<>()).add(u);
users = [
    ("Tom", "Beijing"),
    ("Amy", "Shanghai"),
    ("Bob", "Beijing"),
    ("Dan", "Shanghai"),
    ("Eve", "Shenzhen"),
]
groups = defaultdict(list)
for name, city in users:
    groups[city].append(name)
print(dict(groups))
# {'Beijing': ['Tom', 'Bob'], 'Shanghai': ['Amy', 'Dan'], 'Shenzhen': ['Eve']}

# 用法3：defaultdict(set) 去重分组
tags = [("a", "x"), ("a", "x"), ("a", "y"), ("b", "z")]
tag_map = defaultdict(set)
for k, v in tags:
    tag_map[k].add(v)
print({k: sorted(v) for k, v in tag_map.items()})   # {'a': ['x', 'y'], 'b': ['z']}

# ⚠️ 陷阱：访问不存在的 key 会「顺手创建」它，导致 dict 变大
d = defaultdict(int)
_ = d["missing"]                             # 只是读一下
print(dict(d))                               # {'missing': 0}  ← 被写进去了！
print(len(d))                                # 1

# 只读场景要用 dict.get(k, 0)，或 dict.setdefault（setdefault 行为一样会插入）
print(d.get("nope", 0))                      # 0

# -------------------- deque：双端队列 --------------------
# ⭐⭐ 常用
# Java: ArrayDeque<Integer> / LinkedList<Integer>
from collections import deque

dq = deque([1, 2, 3])
dq.append(4)                                 # 右端入队（= Java 的 addLast）
dq.appendleft(0)                             # 左端入队（= Java 的 addFirst）
print(dq)                                    # deque([0, 1, 2, 3, 4])

# Java: deque.pollFirst() / pollLast()
print(dq.popleft())                          # 0
print(dq.pop())                              # 4
print(dq)                                    # deque([1, 2, 3])

# rotate：整体旋转（Java 的 Collections.rotate，但那是 List 专用且较慢）
dq2 = deque([1, 2, 3, 4, 5])
dq2.rotate(2)                                # 每个元素右移 2 位
print(dq2)                                   # deque([4, 5, 1, 2, 3])
dq2.rotate(-2)                               # 负数左移
print(dq2)                                   # deque([1, 2, 3, 4, 5])

# maxlen：固定长度滑动窗口（Java 要自己判断并 removeFirst）
# 典型场景：保留最近 N 条日志 / 最近 N 次请求耗时
recent = deque(maxlen=3)
for i in range(1, 6):
    recent.append(i)                         # 满了自动从左边丢最旧的
print(recent)                                # deque([3, 4, 5], maxlen=3)

# ⭐⭐⭐ 为什么比 list 做队列快：
# list.pop(0) 要整体搬移后面所有元素 → O(n)
# deque.popleft() 是双向链表 + 块存储 → O(1)
# Java 对照：ArrayList.remove(0) 也是 O(n)，所以 Java 用 ArrayDeque
import timeit

# ⚠️ 注意：必须用 setup 参数预先建好容器，
# 否则 lambda 里「构造容器」的开销会盖过「取元素」的开销，测出来是错的结论
N = 20000
list_time = timeit.timeit("lst.pop(0)", setup=f"lst = list(range({N}))", number=1000)
deque_time = timeit.timeit("dq.popleft()",
                           setup=f"from collections import deque; dq = deque(range({N}))",
                           number=1000)
print(deque_time < list_time)                # True  ← deque 快一个数量级以上

# -------------------- namedtuple：具名元组 --------------------
# ⭐⭐ 常用 —— 对标 Java 14+ record
# Java: record Point(int x, int y) {}
# 区别：namedtuple 是不可变的、轻量的，且能用下标访问
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(1, 2)
print(p)                                     # Point(x=1, y=2)

# 字段访问（Java: p.x()）
print(p.x, p.y)                              # 1 2

# 下标访问（tuple 的老本事，Java record 做不到）
print(p[0], p[1])                            # 1 2

# 解包（Java record 要自己写方法来拆）
px, py = p
print(px, py)                                # 1 2

# _asdict：转成字典（Java 要手写 toMap 或用反射）
# ⚠️ 3.8+ 返回普通 dict，早期版本返回 OrderedDict
print(p._asdict())                           # {'x': 1, 'y': 2}
print(type(p._asdict()))                     # <class 'dict'>

# _replace：基于原对象生成新对象（不可变，不会改原值）
p2 = p._replace(x=10)
print(p2)                                    # Point(x=10, y=2)
print(p)                                     # Point(x=1, y=2)  ← 原对象不变

# _fields：字段名元组（反射用）
print(Point._fields)                         # ('x', 'y')

# ⚠️ 默认值用 defaults 参数（3.7+）
User = namedtuple("User", ["name", "age", "city"], defaults=["未知", "北京"])
print(User("Tom"))                           # User(name='Tom', age='未知', city='北京')

# 应用：函数返回多值时比裸元组可读
def get_range(nums):
    return namedtuple("Range", ["min", "max"])(min(nums), max(nums))

r = get_range([3, 1, 4, 1, 5])
print(r.min, r.max)                          # 1 5

# -------------------- OrderedDict --------------------
# ⭐ 了解 —— 用到再查
# Java: LinkedHashMap 保证插入顺序
# ⚠️ 重点：Python 3.7+ 起，普通 dict 已保证插入顺序，OrderedDict 基本不再需要
from collections import OrderedDict

normal = {"a": 1, "b": 2, "c": 3}
for k in normal:
    print(k, end=" ")                        # a b c   ← 普通 dict 也保序
print()

odd = OrderedDict([("a", 1), ("b", 2)])
# 唯一还有用的场景1：move_to_end（LRU 缓存常用）
odd.move_to_end("a")                         # 把 a 移到末尾
print(odd)                                   # OrderedDict({'b': 2, 'a': 1})
odd.move_to_end("a", last=False)             # last=False 移到开头
print(odd)                                   # OrderedDict({'a': 1, 'b': 2})

# 唯一还有用的场景2：相等性语义 —— OrderedDict 比较时顺序也参与
# 普通 dict 只要键值相同就相等，不管顺序
print({"a": 1, "b": 2} == {"b": 2, "a": 1})  # True
print(OrderedDict([("a", 1), ("b", 2)]) == OrderedDict([("b", 2), ("a", 1)]))   # False

# 结论：日常一律用 dict；只有需要 move_to_end 或顺序敏感的相等判断时才用 OrderedDict

# ==================== 六、itertools 简介 ====================
# ⭐⭐ 常用
# Java: Stream 的中间操作，同为惰性求值
# ⚠️⚠️ 最重要的一点：itertools 全部返回迭代器，只消费一次！
# 这和 Java Stream 完全一致（Stream 也只能消费一次），别想着重复遍历
import itertools

# -------------------- chain：串联多个可迭代对象 --------------------
# Java: Stream.concat(a.stream(), b.stream())
print(list(itertools.chain([1, 2], [3, 4], [5])))     # [1, 2, 3, 4, 5]
# Java: stream().flatMap(List::stream)
print(list(itertools.chain.from_iterable([[1, 2], [3, 4]])))   # [1, 2, 3, 4]

# -------------------- islice：切片迭代器（itertools 版 [start:stop:step]）--------------------
# Java: stream().skip(2).limit(3)
print(list(itertools.islice(range(10), 2, 5)))        # [2, 3, 4]
print(list(itertools.islice(range(10), 3)))           # [0, 1, 2]
print(list(itertools.islice(range(10), 0, 10, 3)))    # [0, 3, 6, 9]

# ⚠️ islice 不能传负数（因为它是惰性的，不知道总长度）
# print(list(itertools.islice(range(10), -3, None)))  # ValueError

# 典型场景：只读大文件前 5 行，不会把整个文件读进内存
# with open("big.log") as f:
#     for line in itertools.islice(f, 5):
#         print(line)

# 惰性证明：只取 3 个，后面的根本不生成
it = itertools.count(1)                               # 无限计数器，类似 for(;;i++)
print(list(itertools.islice(it, 3)))                  # [1, 2, 3]

# -------------------- groupby：分组 --------------------
# ⚠️⚠️ 和 SQL 的 GROUP BY 不同：必须先按 key 排好序，否则相同 key 会被拆成多组
# Java: Collectors.groupingBy
data = [
    ("Beijing", "Tom"),
    ("Shanghai", "Amy"),
    ("Beijing", "Bob"),
    ("Shanghai", "Dan"),
]
# 必须先排序，否则 Beijing 会分成两组
data_sorted = sorted(data, key=operator.itemgetter(0))
for city, group in itertools.groupby(data_sorted, key=operator.itemgetter(0)):
    print(city, [name for _, name in group], end=" | ")
print()   # Beijing ['Tom', 'Bob'] | Shanghai ['Amy', 'Dan'] |

# 对比：defaultdict(list) 不需要排序，日常分组更推荐它
# 需要流式处理（数据已有序 / 数据量大不想全放内存）时才用 groupby

# -------------------- combinations / permutations --------------------
# Java: 没有内置，要自己写回溯
# combinations：组合，不考虑顺序，C(n, r)
print(list(itertools.combinations([1, 2, 3, 4], 2)))
# [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
print(len(list(itertools.combinations([1, 2, 3, 4], 2))))   # 6

# permutations：排列，考虑顺序，A(n, r)
print(list(itertools.permutations([1, 2, 3], 2)))
# [(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]
print(len(list(itertools.permutations([1, 2, 3], 2))))      # 6

# 应用：密码/优惠券码枚举、背包问题暴力解、测试用例组合

# -------------------- product：笛卡尔积 --------------------
# Java: 嵌套 for 循环
print(list(itertools.product("AB", [1, 2])))
# [('A', 1), ('A', 2), ('B', 1), ('B', 2)]

# repeat 参数：自己和自己做笛卡尔积（替代多重循环）
print(list(itertools.product([0, 1], repeat=2)))
# [(0, 0), (0, 1), (1, 0), (1, 1)]

print(list(itertools.product([0, 1], repeat=3)))
# [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]

# 应用：生成测试用例矩阵（多参数组合）
envs = ["dev", "prod"]
browsers = ["chrome", "safari"]
cases = [f"{e}-{b}" for e, b in itertools.product(envs, browsers)]
print(cases)   # ['dev-chrome', 'dev-safari', 'prod-chrome', 'prod-safari']

# -------------------- 惰性求值总结 --------------------
# 以上全部函数返回的都是迭代器，不会立刻计算，也不占内存
print(type(itertools.chain([1], [2])))       # <class 'itertools.chain'>
print(type(itertools.count()))               # <class 'itertools.count'>

# Java 对照：Stream 是惰性的，终端操作（collect/forEach）才触发计算
# Python 对照：list() / for / sum() 等消费动作才触发计算

print("=== 14 内置函数与 collections 结束 ===")
