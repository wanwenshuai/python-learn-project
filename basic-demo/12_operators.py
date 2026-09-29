"""
===== 第12课：运算符与表达式 =====
对标 Java 的运算符，但多了幂运算、整除、链式比较、海象运算符
本课重点：Python 的运算符在几个地方和 Java 行为完全不同，是最容易写出隐蔽 bug 的地方
"""

# ==================== 一、算术运算符 ====================

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: int a = 7 / 2;   // 3（整数除法，直接截断）
# ⚠️ Python 的 / 永远是浮点除法，不会截断！这是 Java 开发者的头号坑
print(7 / 2)            # 3.5（Java 里是 3）
print(6 / 2)            # 3.0（即使整除也返回 float，不是 int）
print(type(6 / 2))      # <class 'float'>

# ⭐⭐⭐ 必会 —— 整除用 //（Java 的 / 在 Python 里对应的是 //）
# Java: int a = 7 / 2;
print(7 // 2)           # 3

# ⚠️ 负数整除：Python 是"向下取整"，Java 是"向零取整"
# Java: 7 / -2 == -3   （向零）
print(-7 // 2)          # -4（向下，不是 -3）
print(7 // -2)          # -4（向下，不是 -3）
# 💡 记法：// 的结果永远 <= 数学上的精确商

# ⭐⭐⭐ 必会 —— 取模 %，负数行为与 Java 不同
# Java: -7 % 3 == -1   （结果的符号跟被除数）
print(-7 % 3)           # 2（结果的符号跟除数，不是 -1！）
print(7 % -3)           # -2
# 💡 这条规则让 Python 的 % 非常适合做"环形"计算（时间、索引、周期）
print(23 % 24)          # 23
print(25 % 24)          # 1（24 小时制，天然循环）

# ⭐⭐⭐ 必会 —— 幂运算 **（Java 没有运算符，要用 Math.pow）
# Java: Math.pow(2, 10) 返回 double；Python 的 ** 返回精确整数
print(2 ** 10)          # 1024
print(2 ** 0.5)         # 1.4142135623730951（开方）
print(10 ** 100)        # 超长整数，Python 自动支持任意精度

# ⭐⭐ 常用 —— 负数与整除的实用场景：分页计算
total, page_size = 95, 10
# Java: int pages = (total + page_size - 1) / page_size;  // 需手动 +size-1
pages = -(-total // page_size)   # 向上取整的惯用写法
print(pages)            # 10
import math
print(math.ceil(total / page_size))   # 10（更直观的写法，推荐）

# ==================== 二、赋值运算符 ====================

# ⭐⭐⭐ 必会 —— ⚠️ Python 没有 ++ 和 -- ！！！
# Java: i++;  i--;
# Python 里写 i++ 会直接报 SyntaxError，必须写 i += 1
count = 0
count += 1              # 自增只能这么写
count += 1
print(count)            # 2

# 支持的增强赋值
n = 10
n -= 3
print(n)                # 7
n *= 2
print(n)                # 14
n //= 4
print(n)                # 3
n **= 3
print(n)                # 27
n %= 5
print(n)                # 2

# ⭐⭐⭐ 必会 —— 多目标赋值（Java 不能连等）
# Java: int a = 0, b = 0;  // 只是声明列表，不是连等
a = b = 0
print(a, b)             # 0 0

# ⚠️ 陷阱：连等赋值给可变对象，多个名字指向同一个对象！
x = y = []              # x 和 y 是同一个 list
x.append(1)
print(y)                # [1]  ← y 也被改了！
print(x is y)           # True
# ✅ 正确写法：分别创建
p, q = [], []
p.append(1)
print(q)                # []

# ⭐⭐ 常用 —— 多重赋值 + 解包（Java 完全做不到）
# Java: int a = 1, b = 2; int tmp = a; a = b; b = tmp;
m, k = 1, 2
m, k = k, m             # 一行交换，靠的是右边先打包成元组
print(m, k)             # 2 1

# ==================== 三、比较运算符 ====================

# ⭐⭐⭐ 必会 —— 链式比较（Java 绝对写不出来）
# Java: if (age >= 18 && age <= 60) { ... }
age = 25
print(18 <= age <= 60)  # True（等价于 18 <= age and age <= 60，但更易读）

# 链式比较的中间值只计算一次，这是它的隐藏优势
print(1 < 2 < 3 < 4)    # True
print(1 < 3 > 2)        # True（不是数学表达式，是逻辑与）

# ⭐⭐⭐ 必会 —— == 比值，is 比身份（Java 里 == 比引用，equals 比值）
# Java: a.equals(b)
list1 = [1, 2, 3]
list2 = [1, 2, 3]
list3 = list1
print(list1 == list2)   # True（值相等）
print(list1 is list2)   # False（不是同一个对象）
print(list1 is list3)   # True（同一个对象）
# ⚠️ 铁律：和 None / True / False 比较永远用 is，不要用 ==
print(None is None)     # True

# ==================== 四、逻辑运算符 ====================

# ⭐⭐⭐ 必会 —— and / or / not（不是 && || !）
# Java: if (a && b) { ... }
flag1, flag2 = True, False
print(flag1 and flag2)  # False
print(flag1 or flag2)   # True
print(not flag1)        # False

# ⭐⭐⭐ 必会 —— ⚠️ 短路求值 + 返回操作数本身（不是布尔！）
# Java 的 && 返回 boolean；Python 的 and/or 返回的是决定结果的那个操作数
print(0 or "默认值")     # 默认值（0 为假，返回右边）
print("" or "默认值")    # 默认值
print("有值" or "默认值")  # 有值（左边为真，直接返回左边，右边不求值）
print(1 and 2)          # 2（左边为真，返回右边）
print(0 and 2)          # 0（左边为假，短路，返回左边）

# 💡 这个特性衍生出两个高频惯用法：
# Java: String name = (input != null && !input.isEmpty()) ? input : "匿名";
name_input = ""
name = name_input or "匿名"      # 一行搞定空值兜底
print(name)                      # 匿名

# Java: if (user != null && user.getAddress() != null) { return user.getAddress().getCity(); }
user = {"address": {"city": "北京"}}
city = user and user.get("address") and user["address"].get("city")
print(city)                      # 北京（链式取值，任一环为空就短路返回）
user2 = None
print(user2 and user2.get("address"))   # None（不会抛异常，Java 这里会 NPE）

# ⚠️ 但代价是：返回值类型不确定，做布尔判断时才安全
print(type(0 or "x"))   # <class 'str'>

# ==================== 五、位运算符 ====================

# ⭐⭐ 常用 —— 位运算和 Java 基本一致
# Java: int r = a & b;
a_bit, b_bit = 0b1100, 0b1010      # 12, 10
print(a_bit & b_bit)    # 8   按位与（0b1000）
print(a_bit | b_bit)    # 14  按位或（0b1110）
print(a_bit ^ b_bit)    # 6   按位异或（0b0110）
print(~a_bit)           # -13 按位取反（Python 是无限位补码，结果和 Java 的 ~12 一致）
print(a_bit << 1)       # 24  左移
print(a_bit >> 1)       # 6   右移

# ⭐⭐ 常用 —— 常用技巧：用位运算做权限标记
# Java: 同样用法，但通常用 EnumSet
READ, WRITE, EXEC = 1, 2, 4
perm = READ | WRITE
print(perm)                     # 3
print(bool(perm & READ))        # True
print(bool(perm & EXEC))        # False
perm |= EXEC
print(perm)                     # 7

# ⚠️ 别混淆：& 和 and 不是一回事，| 和 or 也不是
# Java: 这里 Java 的 & 和 && 也有区别（& 不短路）
print(3 & 1)            # 1（按位与）
print(3 and 1)          # 1（逻辑与，返回操作数）
print(2 & 1)            # 0（按位与）
print(2 and 1)          # 1（逻辑与，2 为真所以返回 1）← 结果不同！

# ==================== 六、成员运算符 ====================

# ⭐⭐⭐ 必会 —— in / not in（Java 的 contains / containsKey）
# Java: list.contains("apple")
fruits = ["apple", "banana"]
print("apple" in fruits)        # True
# Java: map.containsKey("name")
student = {"name": "Alice"}
print("name" in student)        # True（dict 判断的是 key，不是 value）
print("Alice" in student)       # False
# Java: set.contains(3)
print(3 in {1, 2, 3})           # True
# 字符串也是"容器"
print("Py" in "Hello Python")   # True
print("xyz" not in "Hello")     # True

# ⚠️ in 用在 list 上是 O(n) 线性扫描，用在 set/dict 上才是 O(1)
# 大量判断存在性时，把 list 换成 set，这是一条高频性能优化

# ==================== 七、海象运算符 := （3.8+）====================

# ⭐⭐ 常用 —— 赋值表达式：在表达式内部完成赋值
# Java: 无对应语法，只能写成赋值语句再判断

# 场景1：while 循环读数据（Java 要写两遍读取逻辑）
data = iter([1, 2, 3, 0, 4])
# Java: int v; while ((v = read()) != 0) { ... }
result = []
while (v := next(data, 0)) != 0:      # 读一次，判断，同时拿到值
    result.append(v)
print(result)                         # [1, 2, 3]

# 场景2：避免重复计算
text = "  hello  "
if (stripped := text.strip()):
    print(f"处理后的值: {stripped}")   # 处理后的值: hello

# 场景3：推导式里复用计算结果（否则要算两遍）
nums = [1, 2, 3, 4, 5, 6]
result = [y for x in nums if (y := x * x) > 10]
print(result)                         # [16, 25, 36]

# ⚠️ 可读性警示：海象会让代码变"密"，能用普通赋值就别用
# 下面这种写法虽然合法，但不如老老实实分两行
if (m := 10) > 5:
    print(m)                          # 10

# ==================== 八、运算符优先级（⭐ 了解）====================
"""
从高到低，同一行的从左到右：
    **
    +x  -x  ~x                    一元运算符
    *  /  //  %
    +  -                          加减
    <<  >>
    &
    ^
    |
    ==  !=  <  <=  >  >=  is  in  比较（可链式）
    not
    and
    or
    :=                            海象
    lambda

Java 开发者最常出错的地方：not 的优先级比比较运算符低
    Java: !a.equals(b)
    Python: not a == b    等价于 not (a == b)，写成 !a == b 是错的
"""
a, b = 1, 2
print(not a == b)       # True（= not (1 == 2)）
print(not a)            # False

# ⭐ 实用建议：拿不准就加括号。加括号永远不扣分。

# ==================== 九、运算符重载钩子（⭐ 了解）====================
# ⭐⭐ 常用 —— 自定义类可以通过魔法方法重载运算符（第16课详讲）
class Money:
    def __init__(self, amount: float):
        self.amount = amount

    def __add__(self, other):        # 决定 + 的行为
        return Money(self.amount + other.amount)

    def __eq__(self, other):         # 决定 == 的行为
        return self.amount == other.amount

    def __lt__(self, other):         # 决定 < 的行为（排序依赖它）
        return self.amount < other.amount

    def __repr__(self):
        return f"Money({self.amount})"

print(Money(10) + Money(5))          # Money(15)
print(Money(10) == Money(10))        # True
print(Money(5) < Money(10))          # True
print(sorted([Money(3), Money(1), Money(2)]))   # [Money(1), Money(2), Money(3)]

# ==================== 十、常见坑总结（⭐⭐⭐ 必看）====================
"""
1. 没有 ++ / --              → 写 i += 1，写 i++ 直接 SyntaxError
2. / 永远返回 float          → 取整除用 //，Java 的 int/int 在 Python 要写 //
3. 负数整除是向下取整        → -7 // 2 == -4（Java 是 -3）
4. 负数取模符号跟除数        → -7 % 3 == 2（Java 是 -1）
5. and/or 返回操作数不是布尔 → 1 and 2 得 2，用 bool() 强制转换
6. is 和 == 混用            → 判断 None 必须用 is
7. 连等赋值可变对象          → a = b = [] 会共享同一个 list
8. 浮点精度                 → 0.1 + 0.2 != 0.3，金额用 decimal.Decimal（见第2课）
9. 位运算 & 与逻辑 and 混淆  → 2 & 1 得 0，2 and 1 得 1
"""
print(0.1 + 0.2 == 0.3)   # False（浮点数经典问题）

print("=== 12 运算符与表达式 结束 ===")
