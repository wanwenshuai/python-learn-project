"""
===== 第15课：可变性、引用与拷贝 =====
对标 Java 的引用传递 / clone / 不可变对象

本课是 Java 开发者踩坑最多的一课：
  - Python 没有「基本类型」，变量名只是贴在对象上的标签
  - 赋值 = 绑定别名，不是复制
  - 函数传参传的是对象引用（和 Java 一样是值传递，但效果常被误解）
  - 浅拷贝 / 深拷贝 / 默认参数 / [[0]*3]*3 是四大天坑
"""

print('⚠️ 本课会故意触发若干异常用于教学演示，它们都会被 try/except 捕获，控制台出现 Error / Exception 字样属正常现象，脚本退出码为 0\n')

import sys
import gc
import copy
import weakref

# ==================== 一、变量是标签，不是盒子 ====================

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: int a = 10;  → a 是一个「盒子」，盒子里装着 10 这个值本身
#       a = b;       → 把 b 盒子里的 10 复制一份，倒进 a 盒子；之后改 a 不影响 b
# Python: a = 10    → 在堆上创建 int 对象 10，然后让名字 a「指向」它
#       a = b        → 让 a 也指向 b 指向的那个对象（两个名字，一个对象），没有任何复制

a = 10
b = a
print(a, b)                    # 10 10
# id() 返回对象的内存地址（CPython 实现细节，但足以证明身份）
# Java: System.identityHashCode(obj)，但 Java 的基本类型没有「身份」概念
print(id(a) == id(b))          # True  ← a 和 b 是同一个对象

# 关键：让 a 重新指向别的对象，b 不受任何影响（因为是「重新贴标签」，不是「改盒子里的值」）
a = 20
print(a, b)                    # 20 10
print(id(a) == id(b))          # False

# Java 对照：Java 对象赋值 = 复制引用（两个变量指向同一个堆对象）
# Java: List<String> x = new ArrayList<>(); x.add("A");
#       List<String> y = x;              // 复制的是「引用」
#       y.add("B"); System.out.println(x); // [A, B]  ← x 也变了
# Python 完全一样，只是基本类型（int/str）也遵循这套规则
inner_list = ["A"]
x = inner_list
y = x
y.append("B")
print(x)                       # ['A', 'B']  ← 和 Java 的对象赋值一模一样

# Java 对比概括：
#   Java 基本类型赋值  = 复制值        → Python 没有对应物
#   Java 对象赋值      = 复制引用      → Python 的赋值就是这个
#   所以「Python 的 = 是复制」是错的，「Python 的 = 是绑定别名」才对

# ==================== 二、可变 vs 不可变 ====================

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# 不可变（immutable）：创建后内容永远不能变，只能整体换一个新对象
#   int / float / bool / complex / str / bytes / tuple / frozenset / None
# 可变（mutable）：可以原地修改内容，身份（id）不变
#   list / dict / set / bytearray / 自定义对象（默认都是可变的）
#
# Java 对照：
#   不可变 ≈ Java 的 String、Integer、Long、BigDecimal、LocalDate、record（若字段全 final）
#   可变   ≈ Java 的 ArrayList、HashMap、HashSet、普通 POJO

nums = [1, 2, 3]
ints = (1, 2, 3)
text = "abc"
fset = frozenset([1, 2, 3])
print(type(nums).__name__, type(ints).__name__, type(text).__name__, type(fset).__name__)
# list tuple str frozenset

# -------------------- 不可变：str 拼接会产生新对象 --------------------
# ⭐⭐⭐ 必会
# Java: String s = "a"; s = s + "b";  // 同样是产生新 String 对象，原对象不动
#       所以 Java 里循环拼接要用 StringBuilder
s = "a"
old_id = id(s)
s = s + "b"                    # 表面像「修改」，实际是新建 "ab" 再让 s 指向它
print(s)                       # ab
print(id(s) == old_id)         # False  ← 换了对象

# 更直观：两个名字共享同一个 str，拼接后只有一个名字换了对象
p = "hello"
q = p                          # p、q 指向同一个 "hello"
print(p is q)                  # True
p = p + " world"               # p 换新对象，q 原地不动
print(p, "|", q)               # hello world | hello

# -------------------- 可变：list.append 不改变身份 --------------------
# ⭐⭐⭐ 必会
# Java: List<Integer> list = new ArrayList<>(); list.add(4);  // 原地修改
lst = [1, 2, 3]
lst_id = id(lst)
lst.append(4)                  # 原地修改，不产生新 list
print(lst)                     # [1, 2, 3, 4]
print(id(lst) == lst_id)       # True   ← 身份没变

# 反面：list 的 + 号会创建新对象（和 str 一样）
lst2 = [1, 2, 3]
lst2_id = id(lst2)
lst2 = lst2 + [4]
print(lst2)                    # [1, 2, 3, 4]
print(id(lst2) == lst2_id)     # False  ← + 号返回新 list

# 原地扩展用 += 或 extend
lst3 = [1, 2, 3]
lst3_id = id(lst3)
lst3 += [4]                    # list 的 += 等价于 extend，是原地操作
print(lst3)                    # [1, 2, 3, 4]
print(id(lst3) == lst3_id)     # True
# ⚠️ 但 tuple 的 += 是新建对象（tuple 不可变）：
t = (1, 2)
t_id = id(t)
t += (3,)
print(t)                       # (1, 2, 3)
print(id(t) == t_id)           # False

# -------------------- 为什么字符串必须不可变 --------------------
# ⭐ 了解 —— 用到再查
# 1) 可哈希：dict / set 靠 hash 定位元素。若 key 的内容能变，hash 就变了，
#    再也找不到这个 key（Java 里 HashMap 的 key 用可变对象同样会「丢数据」）。
# 2) 可安全共享：字符串驻留（interning）让相同字面量共用一份内存，不可变才敢这么干。
# 3) 线程安全：多线程读同一个 str 不需要加锁（Java 的 String 同理）。
# 4) Java 里 String 也是 final + 不可变，设计动机完全一致。
d = {"key": 1}
# 若 str 可变、且修改了 "key" 的内容，d 里这个 entry 就永远找不到了
print(d["key"])                # 1

# -------------------- 元组的「伪不可变」 --------------------
# ⭐⭐ 常用 —— 经常用
# tuple 只保证「它自己持有的引用」不变，不保证被引用对象的内容不变。
# Java 对照：Collections.unmodifiableList(inner) 放在 final 字段里 —— 外层壳不可变，
#            但内层元素照样能改
t2 = (1, [2, 3])
print(t2)                      # (1, [2, 3])
t2[1].append(4)                # tuple 本身没变，改的是它里面那个 list
print(t2)                      # (1, [2, 3, 4])
# 真·不可变：里面也放不可变对象
t3 = (1, (2, 3))
print(t3)                      # (1, (2, 3))
# frozenset 同理：集合本身不可变，但能塞进……不行，frozenset 要求元素必须可哈希
print(frozenset([1, 2, 3]))    # frozenset({1, 2, 3})

# ==================== 三、`=` 是绑定，不是复制 ====================

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# 这是 Java 开发者最常犯的错：以为 Python 的 = 会复制一份
# Java: List<Integer> a = new ArrayList<>(List.of(1,2,3));
#       List<Integer> b = a;   // 复制引用，同一个对象
alist = [1, 2, 3]
blist = alist                  # 没有复制！只是给同一个 list 起了第二个名字
print(alist is blist)          # True

blist.append(4)
print(alist)                   # [1, 2, 3, 4]  ← 改 b，a 也变
print(blist)                   # [1, 2, 3, 4]

alist[0] = 99
print(blist)                   # [99, 2, 3, 4]  ← 反向也成立

# 想要真正独立的副本，必须显式复制
clist = alist.copy()           # 等价于 list(alist) 或 alist[:]
print(clist is alist)          # False
clist.append(5)
print(alist)                   # [99, 2, 3, 4]     ← 原对象不受影响
print(clist)                   # [99, 2, 3, 4, 5]

# ⚠️ 不可变对象没这个问题：因为「修改」本质是重新绑定，天然互不影响
n1 = 1
n2 = n1
n2 = n2 + 1
print(n1, n2)                  # 1 2

# ==================== 四、函数参数传递 ====================

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# 结论：Python 和 Java 一样，都是「值传递」。
#   传的是「对象引用的副本」—— 也就是把实参的 id 复制一份给形参。
#   形参和实参指向同一个对象 → 改对象内容，外面看得见；
#   给形参重新赋值 → 只是让形参改指向别的对象，外面看不见。
# Java 术语：pass-by-value of the reference（引用传递是误称）

# -------------------- 可变对象：函数内 append 会影响外部 --------------------
# Java: void addOne(List<Integer> l) { l.add(99); }  ← 完全一样的行为
def append_item(target: list, item) -> None:
    print("  形参与实参是同一对象:", id(target) == id(source))
    target.append(item)        # 原地修改

source = [1, 2]
append_item(source, 99)
#   形参与实参是同一对象: True
print(source)                  # [1, 2, 99]  ← 外部被改了

# -------------------- 不可变对象：函数内「修改」不影响外部 --------------------
# Java: void addOne(int n) { n = n + 1; }  ← 完全一样，外面不变
def add_one(n: int) -> int:
    print("  传入时是同一对象:", id(n) == id(num))
    n = n + 1                  # 重新绑定到新对象，不是修改原对象
    print("  +1 后还是同一对象:", id(n) == id(num))
    return n

num = 10
result = add_one(num)
#   传入时是同一对象: True
#   +1 后还是同一对象: False
print(result, num)             # 11 10  ← num 没变

# 上面两段的差别不在「传参方式」，而在「对象是否可变」：
#   list 能原地改 → 外面受影响；int 不能原地改，只能重新绑定 → 外面不受影响

# -------------------- str 的坑：想「在函数里改字符串」 --------------------
def bad_upper(s: str) -> None:
    s = s.upper()              # 只是让局部名字 s 指向了新 str，外面拿不到
    return None

text2 = "abc"
bad_upper(text2)
print(text2)                   # abc  ← 没变
# 正确做法：把新值 return 出去，由调用方接收
def good_upper(s: str) -> str:
    return s.upper()
text2 = good_upper(text2)
print(text2)                   # ABC

# -------------------- 防御性编程：函数里要不要 copy --------------------
# ⭐⭐ 常用 —— 经常用
# 1) 只读不改：不 copy（省性能），但要用类型注解 + 文档说清楚
def total(scores: list) -> int:
    """只读，不修改入参"""
    return sum(scores)

# 2) 要改但不想污染调用方：入口处 copy 一份（Java 里常写 new ArrayList<>(input)）
def normalize(scores: list) -> list:
    data = list(scores)        # 关键一步：先复制，再改副本
    data.sort(reverse=True)
    return data

raw = [70, 90, 80]
print(normalize(raw))          # [90, 80, 70]
print(raw)                     # [70, 90, 80]  ← 原数据完好
print(total(raw))              # 240

# 3) 返回内部集合时也要防御：返回副本，别把内部状态暴露出去
class Team:
    def __init__(self, members):
        self._members = list(members)
    def members(self):
        return list(self._members)   # 返回副本，外部改不动内部
    def add(self, name):
        self._members.append(name)

team = Team(["Alice"])
got = team.members()
got.append("Hacker")           # 改的是副本
print(team.members())          # ['Alice']
team.add("Bob")
print(team.members())          # ['Alice', 'Bob']

# ==================== 五、`is` 与 `==` ====================

# ⭐⭐ 常用 —— 经常用
# == : 比值（调用 __eq__，≈ Java 的 equals()）
# is : 比身份（比 id，≈ Java 的 ==，即比是否是同一个对象）
#
# Java 对照表：
#   Java a == b        → Python a is b
#   Java a.equals(b)   → Python a == b
# 两边的语义正好「反过来」，这是最容易混的地方！

l1 = [1, 2, 3]
l2 = [1, 2, 3]
l3 = l1
print(l1 == l2)                # True   ← 值相等
print(l1 is l2)                # False  ← 不是同一个对象
print(l1 is l3)                # True   ← 同一个对象
print(id(l1) == id(l2))        # False

# -------------------- 小整数缓存（-5 ~ 256）--------------------
# ⭐⭐ 常用 —— 经常用
# CPython 启动时就把 -5 ~ 256 的整数对象创建好放在一个数组里，复用它们
# Java 对照：Integer.valueOf(-128~127) 的缓存，IntegerCache —— 一模一样的套路
i1 = 256
i2 = int("256")                # 运行时从字符串解析，命中缓存 → 拿到同一个对象
print(i1 is i2)                # True
i3 = 257
i4 = int("257")                # 超出缓存范围 → 每次都是新对象
print(i3 is i4)                # False
print(i3 == i4)                # True   ← 值永远相等，身份不一定
# Java: Integer a = 127, b = 127; a == b → true
#       Integer c = 128, d = 128; c == d → false   ← 同一个坑！

# ⚠️ 另一个陷阱：同一个 code object 里的字面量会被去重，所以字面量比较永远为 True
i5 = 257
i6 = 257
print(i5 is i6)                # True   ← 不要因此以为 257 被缓存了！只是常量复用了

# -------------------- 字符串驻留 --------------------
# ⭐ 了解 —— 用到再查
# 编译器把「看起来像标识符」的字符串常量做驻留（interned），相同字面量共用一份
s1 = "hello_world"
s2 = "hello_world"
print(s1 is s2)                # True   ← 驻留 / 同一常量
# 运行时拼出来的字符串不会自动驻留
s3 = "hello world!"
s4 = " ".join(["hello", "world!"])
print(s3 == s4)                # True
print(s3 is s4)                # False  ← 值相同，对象不同
print(sys.intern(s4) is s3)    # False  ← intern 后也未必等于原来那个字面量对象
print(sys.intern("hello world!") is sys.intern("hello world!"))  # True

# -------------------- 铁律 --------------------
# 1) 判断值相等永远用 ==，绝不用 is 比较 int / str / 其他对象
# 2) 判断 None 必须用 is（None 是单例，is 最快且语义正确）
#    Java: obj == null
value = None
print(value is None)           # True
print(value == None)           # True   ← 能跑但不要这么写，PEP8 明确禁止
# 3) 判断「是不是同一个对象」才用 is

# Java 对照：Java 里 `list1 == list2` 比引用，`list1.equals(list2)` 比值 —— 顺序是反的，
#            Python 里 `is` 才是比引用，`==` 比值。记牢别搞混。

# ==================== 六、浅拷贝与深拷贝 ====================

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# 浅拷贝（shallow copy）：只复制最外层容器，内层元素仍然是「同一个对象」
# 深拷贝（deep copy）  ：递归复制所有层级的对象，完全独立
# Java 对照：
#   Object.clone() 默认就是浅拷贝（复制字段引用）
#   深拷贝 Java 必须手写（递归 clone / 序列化反序列化 / 第三方库），
#   Python 内置 copy.deepcopy 一行搞定

# -------------------- 5 种浅拷贝写法 --------------------
# Java 对照：new ArrayList<>(list) / list.clone() / stream().collect(toList())
nested = [[1, 2], [3, 4]]
sh1 = copy.copy(nested)        # 1. 通用浅拷贝（任何对象都能用）
sh2 = nested.copy()            # 2. list / dict / set 自带的 copy()
sh3 = list(nested)             # 3. list() 构造器（≈ Java new ArrayList<>(list)）
sh4 = nested[:]                # 4. 全切片（Python 特有，最常用的简写）
sh5 = copy.copy(nested)        # 5. copy.copy 的重复调用（结果同 sh1，仅作对照）

print(sh1 is nested, sh2 is nested, sh3 is nested, sh4 is nested)  # False False False False
print(sh5 is nested)           # False  ← 5 种写法都产生了新容器
print(sh1 == nested, sh2 == nested)                               # True True

# dict / set 也有自己的 copy
d0 = {"a": 1}
print(d0.copy() is d0)         # False
print(d0.copy() == d0)         # True
st0 = {1, 2}
print(st0.copy() is st0)       # False

# -------------------- 浅拷贝的坑 --------------------
# 外层是新的，内层还是共享的
print(id(sh1) == id(nested))   # False  ← 外层独立
print(id(sh1[0]) == id(nested[0]))  # True   ← 内层共享！

sh1[0].append(99)              # 改内层
print(sh1)                     # [[1, 2, 99], [3, 4]]
print(nested)                  # [[1, 2, 99], [3, 4]]  ← 原对象被污染了！

# 只替换外层元素则互不影响
sh1[0] = ["new"]
print(sh1)                     # [['new'], [3, 4]]
print(nested)                  # [[1, 2, 99], [3, 4]]  ← 原对象不受影响

# -------------------- 深拷贝 --------------------
deep = copy.deepcopy(nested)
print(id(deep) == id(nested))          # False
print(id(deep[0]) == id(nested[0]))    # False  ← 内层也独立了
deep[0].append(1000)
print(deep)                    # [[1, 2, 99, 1000], [3, 4]]
print(nested)                  # [[1, 2, 99], [3, 4]]  ← 完全不受影响

# 三层嵌套也照样递归复制
lvl3 = [[[1]]]
d3 = copy.deepcopy(lvl3)
print(id(d3[0]) == id(lvl3[0]))        # False
print(id(d3[0][0]) == id(lvl3[0][0]))  # False

# -------------------- 特例：不可变对象直接返回自身（优化） --------------------
# 不可变对象的拷贝没有意义，copy 会直接返回原对象（省内存）
tup = (1, 2, 3)
print(copy.copy(tup) is tup)           # True
print(copy.deepcopy(tup) is tup)       # True
literal_str = "abc"            # 用变量比较，避免 is 字面量带来的 SyntaxWarning
literal_int = 1
print(copy.copy(literal_str) is literal_str)   # True
print(copy.copy(literal_int) is literal_int)   # True
# 但 tuple 里如果有可变元素，deepcopy 仍会复制内层
tup2 = (1, [2])
print(copy.deepcopy(tup2)[1] is tup2[1])  # False

# -------------------- deepcopy 的代价与选择 --------------------
# ⭐⭐ 常用 —— 经常用
# deepcopy 要递归遍历整个对象图 + 维护 memo 表，慢且吃内存；
# 而且遇到「自引用」「打开的文件句柄」「数据库连接」「锁」会出错或复制出无意义的副本。
# 选择原则：
#   1) 只有一层嵌套（list[str]、dict[str,int]） → 浅拷贝足够，甚至可以用 list(x)
#   2) 深层嵌套且要做「快照 / 回滚」        → deepcopy
#   3) 性能敏感的大对象                    → 手工构造新对象，别 deepcopy
#   4) 循环引用：deepcopy 能正确处理（内部有 memo 表），不会无限递归
cyclic = [1]
cyclic.append(cyclic)          # 自己引用自己
c_copy = copy.deepcopy(cyclic) # 不会栈溢出
print(c_copy[0], c_copy[1] is c_copy)  # 1 True  ← 副本内部依然自引用

# 性能实测（只演示量级差异）
import time
big = [[i for i in range(100)] for _ in range(1000)]
t_start = time.perf_counter()
for _ in range(100):
    copy.copy(big)
shallow_cost = time.perf_counter() - t_start
t_start = time.perf_counter()
for _ in range(100):
    copy.deepcopy(big)
deep_cost = time.perf_counter() - t_start
print("deepcopy 更慢:", deep_cost > shallow_cost)   # deepcopy 更慢: True

# ==================== 七、两个经典陷阱 ====================

# ⭐⭐⭐ 必会 —— 面试必问，生产必炸

# -------------------- 陷阱1：[[0] * 3] * 3 --------------------
# * 号复制的是「引用」，不是「对象」
bad_grid = [[0] * 3] * 3       # ❌ 三行是同一个 list 对象
print(bad_grid)                # [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
print(id(bad_grid[0]) == id(bad_grid[1]))   # True
print(id(bad_grid[1]) == id(bad_grid[2]))   # True
bad_grid[0][0] = 1             # 只想改第一行第一个
print(bad_grid)                # [[1, 0, 0], [1, 0, 0], [1, 0, 0]]  ← 三行全变了！

# Java 类比：List<List<Integer>> g = new ArrayList<>();
#           List<Integer> row = new ArrayList<>(List.of(0,0,0));
#           for (int i=0;i<3;i++) g.add(row);   // 加的是同一个 row 的引用 → 同样的 bug

# ✅ 正确写法1：推导式，每次迭代都新建一个 list
good_grid = [[0] * 3 for _ in range(3)]
print(id(good_grid[0]) == id(good_grid[1]))  # False
good_grid[0][0] = 1
print(good_grid)               # [[1, 0, 0], [0, 0, 0], [0, 0, 0]]

# ✅ 正确写法2：显式循环创建
good_grid2 = []
for _ in range(3):
    good_grid2.append([0] * 3)
good_grid2[0][0] = 1
print(good_grid2)              # [[1, 0, 0], [0, 0, 0], [0, 0, 0]]

# ⚠️ 对比：一维的 [0] * 3 是安全的，因为 0 是不可变对象，复制引用不会出问题
row_ok = [0] * 3
row_ok[0] = 9
print(row_ok)                  # [9, 0, 0]
# ⚠️ 但 ["" ] * 3、[None] * 3 安全；[[]] * 3、[{}] * 3 全部是坑
bad2 = [[]] * 3
bad2[0].append("x")
print(bad2)                    # [['x'], ['x'], ['x']]

# -------------------- 陷阱2：默认参数用可变对象 --------------------
# 默认值只在「函数定义时」求值一次，之后被所有调用共享（存在函数的 __defaults__ 里）
# Java 没有默认参数（靠重载），所以 Java 开发者完全没这个直觉，最容易中招
# Java 类比：static final List<String> CACHE = new ArrayList<>(); 所有调用共用一份

def bad_append(item, bucket=[]):     # ❌
    bucket.append(item)
    return bucket

print(bad_append("a"))         # ['a']
print(bad_append("b"))         # ['a', 'b']   ← 不是 ['b']！上次的数据还在
print(bad_append("c"))         # ['a', 'b', 'c']
# 铁证：默认值就存在函数对象上
print(bad_append.__defaults__) # (['a', 'b', 'c'],)

# ✅ 正确写法：默认 None，函数内判断后新建
def good_append(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket

print(good_append("a"))        # ['a']
print(good_append("b"))        # ['b']
print(good_append.__defaults__)  # (None,)

# ✅ 如果确实想用可变默认值做缓存，写清楚是有意为之（显式传参或挂到函数属性上）
def cached_append(item, bucket=None):
    if bucket is None:
        bucket = cached_append.cache     # 显式共享的缓存
    bucket.append(item)
    return bucket
cached_append.cache = []
print(cached_append("x"))      # ['x']
print(cached_append("y"))      # ['x', 'y']  ← 这是故意的

# 同类陷阱：类属性存可变对象，被所有实例共享
class BadCounter:
    items = []                 # ❌ 类属性，所有实例共享同一个 list
class GoodCounter:
    def __init__(self):
        self.items = []        # ✅ 实例属性，每个实例独立

bc1, bc2 = BadCounter(), GoodCounter()
bc1.items.append(1)
print(BadCounter.items)        # [1]
print(BadCounter.items is bc1.items)  # True
gc1, gc2 = GoodCounter(), GoodCounter()
gc1.items.append(1)
print(gc1.items, gc2.items)    # [1] []

# ==================== 八、原地修改 vs 返回新对象 ====================

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Python 的约定（PEP8 精神）：
#   原地修改的方法 → 返回 None
#   返回新对象的方法 → 不改原对象
# 目的：让你一眼看出「这个调用有没有副作用」。Java 没有这个约定，所以最容易写出 bug。

# -------------------- sort() vs sorted() --------------------
# Java: Collections.sort(list);              // 原地，返回 void
#       list.stream().sorted().collect(...) // 返回新集合
nums2 = [3, 1, 2]
ret = nums2.sort()             # 原地排序，返回 None
print(ret)                     # None
print(nums2)                   # [1, 2, 3]

# ❌ 经典 bug：把返回值赋回去，得到 None
nums3 = [3, 1, 2]
nums3 = nums3.sort()           # 本意是排序，结果 nums3 变成 None
print(nums3)                   # None
# 后续再操作就炸：nums3.append(4) → AttributeError: 'NoneType' object has no attribute 'append'

# ✅ 正确写法1：原地排序，不要接返回值
nums4 = [3, 1, 2]
nums4.sort()
print(nums4)                   # [1, 2, 3]

# ✅ 正确写法2：要新列表就用 sorted()
nums5 = [3, 1, 2]
new_nums = sorted(nums5)       # 返回新 list，原列表不动
print(new_nums)                # [1, 2, 3]
print(nums5)                   # [3, 1, 2]

# -------------------- 一堆「返回 None」的原地方法 --------------------
items = [1]
print(items.append(2))         # None   ← 原地
print(items)                   # [1, 2]
print(items.extend([3]))       # None
print(items)                   # [1, 2, 3]
print(items.insert(0, 0))      # None
print(items)                   # [0, 1, 2, 3]
print(items.remove(0))         # None
print(items)                   # [1, 2, 3]
print(items.reverse())         # None
print(items)                   # [3, 2, 1]

dm = {"a": 1}
print(dm.update({"b": 2}))     # None
print(dm)                      # {'a': 1, 'b': 2}
print(dm.setdefault("c", 3))   # 3      ← 例外：setdefault 返回的是值，不是 None
print(dm)                      # {'a': 1, 'b': 2, 'c': 3}
print(dm.pop("c"))             # 3      ← pop 返回被删的值
print(dm)                      # {'a': 1, 'b': 2}

sm = {1, 2}
print(sm.add(3))               # None
print(sm)                      # {1, 2, 3}
print(sm.discard(1))           # None
print(sm)                      # {2, 3}

# -------------------- 返回新对象的方法（不改原对象）--------------------
src = [3, 1, 2]
print(sorted(src))             # [1, 2, 3]
print(src)                     # [3, 1, 2]
print(src + [9])               # [3, 1, 2, 9]
print(src)                     # [3, 1, 2]
s_src = "abc"
print(s_src.upper(), s_src.replace("a", "z"), s_src)  # ABC zbc abc
print(list(reversed(src)))     # [2, 1, 3]   ← reversed 返回迭代器，不原地改
print(src)                     # [3, 1, 2]

# 字符串全部方法都返回新对象（不可变），这是 Java 开发者最熟悉的部分
print(s_src.strip(), s_src.split("b"), s_src)  # abc ['a', 'c'] abc

# -------------------- 自定义类也遵守这个约定 --------------------
class Stack:
    def __init__(self):
        self._data = []
    def push(self, item) -> None:      # 原地修改 → 返回 None，调用方别接返回值
        self._data.append(item)
    def to_list(self) -> list:         # 计算 / 转换 → 返回新对象
        return list(self._data)        # 返回副本，保护内部状态

stk = Stack()
print(stk.push(1))             # None
stk.push(2)
print(stk.to_list())           # [1, 2]

# ==================== 九、del 与内存 ====================

# ⭐ 了解 —— 用到再查
# CPython 用「引用计数」为主 + 分代 GC 兜底（Java 用可达性分析，没有引用计数）
# del 删的是「名字（引用）」，不是对象；引用计数归零，对象才被立刻回收

# Java 对照：Java 没有 del；obj = null 只是去掉一个引用，回收完全交给 GC，时机不确定。
#           Python 的 CPython 实现下，refcount 归零是「立即」回收（会立刻调用 __del__）。

# -------------------- 引用计数 --------------------
def ref_count_demo():
    data = [1, 2, 3]
    # getrefcount 本身也会 +1，所以「只有自己」时是 1 + 1 = 2
    print(sys.getrefcount(data))       # 2
    alias1 = data                      # 多一个名字
    print(sys.getrefcount(data))       # 3
    alias2 = data                      # 再多一个名字
    print(sys.getrefcount(data))       # 4
    return None

ref_count_demo()               # 依次打印 2 / 3 / 4

# -------------------- del 删名字，不删对象 --------------------
obj = [1, 2, 3]
backup = obj                   # 两个名字指向同一个对象
del obj                        # 只删掉 obj 这个名字
print(backup)                  # [1, 2, 3]  ← 对象还活着，因为 backup 还指着它
# obj 这个名字已经不存在了，再访问会 NameError（注意：这段被 try 包住，不会中断程序）
try:
    print(obj)                 # 不会执行到这里
except NameError as e:
    print("NameError:", e)     # NameError: name 'obj' is not defined

# del 也能删容器里的元素（这个是真的改对象）
bag = [1, 2, 3]
del bag[0]
print(bag)                     # [2, 3]

# -------------------- 循环引用：引用计数的盲区 --------------------
# 两个对象互相引用，即使外部全部 del，refcount 也都不为 0 → 需要 gc 模块出手
class Node:
    def __init__(self, name):
        self.name = name
        self.peer = None

n1 = Node("A")
n2 = Node("B")
n1.peer = n2
n2.peer = n1                   # 互相引用
watcher = weakref.ref(n1)      # 弱引用：不增加 refcount，只用来观察对象是否还活着
print(watcher() is not None)   # True
del n1, n2                     # 外部名字都删了，但两个对象互相引用 → 存活
print(watcher() is not None)   # True   ← 没被回收！
print(gc.collect() > 0)        # True   ← 手动触发 GC，循环引用被清理
print(watcher() is None)       # True   ← 现在真的回收了

# gc 模块常用接口
print(gc.isenabled())          # True   ← 默认开启
print(gc.get_threshold())      # (2000, 10, 10)  ← 第0代分配-释放差值达 2000 触发

# -------------------- 什么时候要关心这些 --------------------
# 1) 长期运行的服务：循环引用 + __del__ 可能造成内存缓慢增长（≈ Java 内存泄漏）
# 2) 大对象（几十 MB 的 list / dict）：早点 del 掉别名，让内存立刻还给系统
# 3) 一般业务代码不用手动 gc.collect()，交给解释器即可（≈ Java 不用 System.gc()）
# 4) 排查内存问题：tracemalloc / objgraph / gc.get_objects()

print("=== 15 可变性、引用与拷贝 结束 ===")
