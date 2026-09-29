"""
===== 第13课：语法糖大全 =====
对标 Java：下面这些写法 Java 要么完全没有，要么要写一大堆样板代码
本课把 Python 的"一行流"集中列出来，并标注哪些是日常高频、哪些只是炫技
"""

# ==================== 一、解包（Unpacking）====================

# ⭐⭐⭐ 必会 —— 可迭代对象可以直接摊开赋值
# Java: String name = pair.getKey(); int age = pair.getValue();
point = (3, 4)
x, y = point
print(x, y)             # 3 4

# 列表一样能解包
first, second, third = [10, 20, 30]
print(first, second, third)     # 10 20 30

# ⭐⭐⭐ 必会 —— 一行交换变量（Java 必须借临时变量）
# Java: int tmp = a; a = b; b = tmp;
a, b = 1, 2
a, b = b, a
print(a, b)             # 2 1

# ⭐⭐⭐ 必会 —— 星号收集剩余元素（Java 只能手动 subList）
first, *rest = [1, 2, 3, 4, 5]
print(first)            # 1
print(rest)             # [2, 3, 4, 5]（注意是 list）

*init, last = [1, 2, 3, 4, 5]
print(init)             # [1, 2, 3, 4]
print(last)             # 5

head, *middle, tail = [1, 2, 3, 4, 5]
print(head, middle, tail)       # 1 [2, 3, 4] 5

# ⭐⭐ 常用 —— 函数返回多值直接解包（本质返回元组，见第6课）
def get_user():
    return "Alice", 25, "alice@example.com"

name, age, email = get_user()
print(name, age, email)         # Alice 25 alice@example.com

# ⭐⭐ 常用 —— 只想要其中一个值时用 _ 占位
_, age_only, _ = get_user()
print(age_only)                 # 25
# 💡 _ 只是个普通变量名，是"约定俗成的垃圾桶"。它真的会被赋值，只是你承诺不用它

# ⭐ 了解 —— 嵌套解包
(data, (lat, lng)) = ("北京", (39.9, 116.4))
print(data, lat, lng)           # 北京 39.9 116.4

# ==================== 二、星号在调用与构造中的解包 ====================

# ⭐⭐⭐ 必会 —— 调用函数时用 * / ** 摊开参数
# Java: method(array) 需要手动循环或重载
def add3(p1, p2, p3):
    return p1 + p2 + p3

args = [1, 2, 3]
print(add3(*args))              # 6（等价于 add3(1, 2, 3)）

kwargs = {"p1": 1, "p2": 2, "p3": 3}
print(add3(**kwargs))           # 6（等价于 add3(p1=1, p2=2, p3=3)）

# ⭐⭐⭐ 必会 —— 合并列表 / 元组
list_a, list_b = [1, 2], [3, 4]
print([*list_a, *list_b])       # [1, 2, 3, 4]
print([*list_a, 99, *list_b])   # [1, 2, 99, 3, 4]（中间还能插值）

# ⭐⭐⭐ 必会 —— 合并字典（Java 要 putAll 或 Stream 拼接）
dict_a = {"a": 1, "b": 2}
dict_b = {"b": 99, "c": 3}
print({**dict_a, **dict_b})     # {'a': 1, 'b': 99, 'c': 3}（后者覆盖前者）
# Python 3.9+ 的更简洁写法：|
print(dict_a | dict_b)          # {'a': 1, 'b': 99, 'c': 3}
# 💡 注意 | 返回新字典，不修改原字典；|= 才是原地更新

# ⭐⭐ 常用 —— 合并集合
print({*{1, 2}, *{2, 3}})       # {1, 2, 3}

# ⭐⭐⭐ 必会 —— print 的 sep / end 参数（Java 要手动拼字符串）
# Java: String.join(",", list)
print(*[1, 2, 3], sep=", ")     # 1, 2, 3
print("加载中", end="")
print("...")                    # 加载中...（不换行）

# ==================== 三、函数签名里的 / 和 *（⭐⭐ 常用）====================

# ⭐⭐ 常用 —— / 之前是"只能按位置传"，* 之后是"只能按关键字传"
# Java: 无对应，Java 的参数总是可以按位置传
def create_order(dish, qty, /, *, spicy=False, note="无"):
    return f"{dish} x{qty} 辣={spicy} 备注={note}"

print(create_order("牛肉面", 2))                      # 牛肉面 x2 辣=False 备注=无
print(create_order("牛肉面", 2, spicy=True))          # 牛肉面 x2 辣=True 备注=无
# create_order(dish="牛肉面", qty=2)   # ❌ TypeError：/ 前面不允许按关键字传
# create_order("牛肉面", 2, True)      # ❌ TypeError：* 后面必须写参数名

# 💡 实际用途：强制调用方写明参数名，避免 create_order(x, y, True, "无") 这种看不懂的调用

# ==================== 四、切片语法糖 ====================

# ⭐⭐⭐ 必会 —— 切片基础（第3、4课讲过，这里补进阶用法）
nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print(nums[2:5])        # [2, 3, 4]
print(nums[::2])        # [0, 2, 4, 6, 8]
print(nums[::-1])       # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]（反转）
print(nums[-3:])        # [7, 8, 9]（最后三个）

# ⭐⭐⭐ 必会 —— 切片赋值（Java 只能 subList().clear() + addAll()）
lst = [1, 2, 3, 4, 5]
lst[1:3] = [20, 30, 40]         # 替换，长度可以不一样！
print(lst)              # [1, 20, 30, 40, 4, 5]

lst[1:4] = []                   # 删除一段（等价于 del lst[1:4]）
print(lst)              # [1, 4, 5]

# ⭐⭐ 常用 —— 切片是"浅拷贝"（第15课详讲深浅拷贝）
original = [1, 2, 3]
copied = original[:]
copied.append(4)
print(original)         # [1, 2, 3]（原列表不受影响）
print(copied)           # [1, 2, 3, 4]

# ⭐ 了解 —— slice 对象：把切片存起来复用
s = slice(1, 3)
print(nums[s])          # [1, 2]

# 💡 字符串也能切片，但字符串不可变，不能做切片赋值（对比 Java 的 substring）
text = "Hello Python"
print(text[6:] + " " + text[:5])        # Python Hello

# ==================== 五、推导式全家桶 ====================

# ⭐⭐⭐ 必会 —— 列表推导式
# Java: list.stream().map(x -> x * 2).collect(Collectors.toList())
print([x * 2 for x in range(5)])            # [0, 2, 4, 6, 8]

# ⭐⭐⭐ 必会 —— 带过滤
# Java: .filter(x -> x % 2 == 0)
print([x for x in range(10) if x % 2 == 0])  # [0, 2, 4, 6, 8]

# ⭐⭐ 常用 —— 多个 if 等价于 and（不要写 and，会变慢且更绕）
print([x for x in range(20) if x % 2 == 0 if x % 3 == 0])   # [0, 6, 12, 18]

# ⭐⭐⭐ 必会 —— if-else 写在 for 前面（三元形态）
print([x if x % 2 == 0 else -x for x in range(6)])          # [0, -1, 2, -3, 4, -5]
# 💡 记忆口诀：if 在 for 后面 = 过滤；if 在 for 前面 = 变形

# ⭐⭐⭐ 必会 —— 字典推导式（Java 要 Collectors.toMap）
# Java: map.entrySet().stream().collect(Collectors.toMap(Map.Entry::getKey, e -> e.getValue().length()))
words = ["apple", "banana", "cherry"]
print({w: len(w) for w in words})           # {'apple': 5, 'banana': 6, 'cherry': 6}

# 反转字典（key 和 value 互换）
scores = {"Alice": 90, "Bob": 85}
print({v: k for k, v in scores.items()})    # {90: 'Alice', 85: 'Bob'}

# ⭐⭐ 常用 —— 集合推导式
print({x % 3 for x in range(10)})           # {0, 1, 2}（自动去重）

# ⭐⭐⭐ 必会 —— 生成器表达式（圆括号，惰性求值，第11课讲过）
gen = (x * x for x in range(1000000))       # 几乎不占内存
print(next(gen), next(gen))                 # 0 1
# 💡 数据量大、只遍历一次 → 用生成器；需要反复用、需要 len/索引 → 用列表

# ⭐⭐ 常用 —— 嵌套推导式：矩阵转置
# Java: 双层 for 循环 + 临时变量
matrix = [[1, 2, 3], [4, 5, 6]]
transposed = [[row[i] for row in matrix] for i in range(3)]
print(transposed)                           # [[1, 4], [2, 5], [3, 6]]

# ⭐ 了解 —— 推导式里用海象避免重复计算
print([z for x in range(10) if (z := x ** 2) > 50])         # [64, 81]

# ⚠️ 推导式可读性红线：
# - 超过两层嵌套 → 拆成普通循环
# - 有复杂逻辑（多个 if-else、函数调用） → 拆成普通循环
# 下面这种"炫耀式"写法在生产代码里会被 review 打回：
#   [y for y in (x.strip() for x in line.split(",") if x) if y.startswith("a")]

# ==================== 六、f-string 进阶 ====================

# ⭐⭐⭐ 必会 —— 格式说明符（Java: String.format("%.2f", x)）
pi = 3.14159265
print(f"{pi:.2f}")          # 3.14（保留两位小数）
print(f"{pi:.0f}")          # 3（四舍五入）
print(f"{1234567:,}")       # 1,234,567（千分位）
print(f"{0.856:.1%}")       # 85.6%（百分比）

# ⭐⭐⭐ 必会 —— 对齐与填充（Java: String.format("%-10s|", s)）
label = "总数"
print(f"[{label:>10}]")     # [        总数]（右对齐，中文按字符数算）
print(f"[{label:<10}]")     # [总数        ]（左对齐）
print(f"[{label:^10}]")     # [    总数    ]（居中）
print(f"[{label:*^10}]")    # [****总数****]（自定义填充字符）
print(f"{42:08d}")          # 00000042（补前导零，Java 的 %08d）
print(f"{255:b} {255:o} {255:x} {255:X}")   # 11111111 377 ff FF（二/八/十六进制）

# ⭐⭐⭐ 必会 —— 调试写法 {x=}（3.8+）：直接打印"表达式 = 值"
# Java: System.out.println("count = " + count);
count = 42
print(f"{count=}")          # count=42
print(f"{count * 2=}")      # count * 2=84（表达式也支持）
# 💡 调试神器，比 print("count =", count) 更省事，还能看出到底是哪个表达式

# ⭐⭐ 常用 —— 转换符 !r / !s / !a
name = "Alice"
print(f"{name!r}")          # 'Alice'（带引号，等价 repr()）
print(f"{name!s}")          # Alice（等价 str()）

# ⭐⭐⭐ 必会 —— 日期格式化（Java: DateTimeFormatter）
import datetime
now = datetime.datetime(2026, 9, 20, 14, 30, 0)
print(f"{now:%Y-%m-%d %H:%M:%S}")       # 2026-09-20 14:30:00
print(f"{now:%Y年%m月%d日}")            # 2026年09月20日

# ⭐⭐ 常用 —— 嵌套引号（3.12+ 允许内外用同种引号）
data = {"key": "value"}
print(f"{data["key"]}")     # value（3.12 之前这里必须用单引号包裹）

# ==================== 七、条件表达式 ====================

# ⭐⭐⭐ 必会 —— 三元表达式（Java: cond ? a : b）
age = 20
print("成年" if age >= 18 else "未成年")     # 成年

# ⭐⭐ 常用 —— 用在赋值和函数默认值上
# Java: String role = isAdmin ? "管理员" : "普通用户";
is_admin = False
role = "管理员" if is_admin else "普通用户"
print(role)                 # 普通用户

# ⚠️ 嵌套三元很可读性差，层级超过一层就该改写成 if-elif
score = 85
# 不推荐：grade = "A" if score >= 90 else "B" if score >= 80 else "C"
# 推荐：
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
else:
    grade = "C"
print(grade)                # B

# 💡 三元 vs and/or：
#   a if cond else b  → 明确、安全、任何值都能用
#   a or b            → 只在"a 为假值就用 b 兜底"时用，a 为 0/""/[] 也会被替换
value = 0
print(value or "兜底")                  # 兜底（0 被当成假值，可能不是你想要的）
print(value if value is not None else "兜底")   # 0（明确判断 None，更安全）

# ==================== 八、其他高频语法糖 ====================

# ⭐⭐⭐ 必会 —— 真值判断简写（Java: if (list != null && !list.isEmpty())）
items = []
if not items:               # 空列表、空字符串、空字典、0、None 都走这里
    print("集合为空")       # 集合为空

# ⭐⭐⭐ 必会 —— with 同时管理多个资源（Java: try-with-resources 嵌套两层）
import tempfile
from pathlib import Path
with tempfile.TemporaryDirectory() as tmp:
    p1, p2 = Path(tmp) / "a.txt", Path(tmp) / "b.txt"
    with open(p1, "w", encoding="utf-8") as f1, open(p2, "w", encoding="utf-8") as f2:
        f1.write("第一个文件")
        f2.write("第二个文件")
    print(p1.read_text(encoding="utf-8"), p2.read_text(encoding="utf-8"))   # 第一个文件 第二个文件
# 💡 目录已自动清理，无需手动删

# ⭐⭐⭐ 必会 —— 链式比较（第12课讲过，这里是它最实用的场景）
score = 85
print(0 <= score <= 100)    # True

# ⭐⭐ 常用 —— 函数隐式返回 None（Java 必须写 return;）
def log(msg):
    print(f"[LOG] {msg}")   # 没有 return，返回 None

print(log("测试"))          # [LOG] 测试 然后输出 None
# 💡 所以 print(函数()) 常常多出一个 None，这是新手最常见的小困惑

# ⭐⭐ 常用 —— 一行读取文件全部内容（对比 Java Files.readString）
with tempfile.TemporaryDirectory() as tmp:
    f = Path(tmp) / "demo.txt"
    f.write_text("hello\nworld", encoding="utf-8")
    print(f.read_text(encoding="utf-8").splitlines())   # ['hello', 'world']
    print(len(f.read_text(encoding="utf-8").splitlines()))  # 2

# ⭐⭐ 常用 —— 空操作 pass（Java 用 ; 或 {}）
def todo_later():
    pass                    # 占位，避免缩进块为空导致语法错误

class Empty:
    pass

print(todo_later())         # None
print(Empty())              # 输出示例：<__main__.Empty object at 0x10102da90>（地址每次不同）

# ==================== 九、语法糖使用原则（⭐⭐⭐ 必读）====================
"""
用语法糖的判断标准，只有一条：写完三个月后你还看得懂吗？

✅ 放心用（团队里人人都在用，属于"普通话"）：
   - 解包 a, b = b, a
   - 推导式（一层，最多带一个 if）
   - f-string 及其格式符
   - 三元表达式（不嵌套）
   - with 多资源
   - 星号解包合并 list/dict
   - 真值判断 if not items

⚠️ 谨慎用（写之前想一下读者）：
   - 海象运算符 :=        → 容易让表达式变密
   - 嵌套推导式           → 超过两层就拆成循环
   - / 和 * 参数分隔符    → 团队没约定就别引入
   - 链式 and/or 取值     → 短路取值很妙但类型不清晰，建议配个注释

❌ 别用（炫技，review 会被打回）：
   - 一行写完整算法（列表推导里塞三四个条件和函数调用）
   - 嵌套三元表达式
   - 用 and/or 替代 if-else 做流程控制
   - 过度使用 _ 导致看不出丢了什么数据

Java 对比总结：
   Java 的哲学是"一种操作只有一种写法"（显式、冗长、好读）
   Python 的哲学是"提供多种写法，但约定俗成只有一种常用"（PEP 8 有云：可读性很重要）
   作为 Java 开发者，先把 ✅ 那一栏用熟，再考虑 ⚠️ 那一栏，永远别碰 ❌
"""

print("=== 13 语法糖大全 结束 ===")
