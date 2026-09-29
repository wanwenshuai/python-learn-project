"""
===== 第2课：数据类型 =====
对标 Java 的 8 种基本类型 + 包装类
"""

# Python 没有 int/char/boolean 之分，一切都是对象
# ⭐⭐⭐ 必会 —— import 导入模块（对应 Java 的 import）
import sys
from decimal import Decimal

# === 数值类型 ===
# ⭐⭐⭐ 必会 —— type() 查看对象类型（类似 Java 的 getClass）
# Java 有 byte/short/int/long/float/double，Python 只有 int/float/complex
i = 42            # int（无限精度，Java long 有上限）
print(type(i))    # <class 'int'>，类似 Java 的 instanceof

# ⭐⭐ 常用 —— int 是任意精度，不会像 Java long 那样溢出
# int 可以任意大（Java BigInteger 的平替）
big = 10 ** 100
print(f"大整数长度: {len(str(big))} 位")

# ⭐⭐⭐ 必会 —— float 就是 Java 的 double（Python 没有单精度类型）
f = 3.14          # float（即 Java 的 double）
print(type(f))    # <class 'float'>

# ⭐ 了解 —— complex 复数类型（Java 需借助第三方库）
c = 1 + 2j        # complex（Java 没有，需用第三方库）
print(c.real, c.imag)  # 实部 1.0, 虚部 2.0

# === 布尔类型 ===
# ⭐⭐⭐ 必会 —— 只有 True/False（首字母大写），且 bool 是 int 的子类
# Java: boolean flag = true;
flag = True   # 大写 T/F！内部是 int 的子类：True=1, False=0
print(True + 1)   # 2

# === None ===
# ⭐⭐⭐ 必会 —— None 表示空值，判空必须用 is，不要用 ==
# Java: Object x = null;
n = None           # Python 的 null
print(type(n))     # <class 'NoneType'>
# 注意：None 不是 False，也不是 0
if n is None:      # 判空用 is，不用 ==
    print("n 是 None")

# === 类型转换 ===
# ⭐⭐⭐ 必会 —— int() / float() / str() 显式转换（对应 parseInt / valueOf）
# Java: Integer.parseInt("42"), String.valueOf(42)
s = "42"
a = "2"

n_int = int(s)      # "42" → 42
f2 = float("3.14")  # "3.14" → 3.14
s2 = str(42)        # 42 → "42"
print(n_int, f2, s2)

# === 类型判断 ===
# ⭐⭐ 常用 —— isinstance() 判断类型（对应 Java 的 instanceof）
# Java: if (x instanceof String)
print(isinstance("hello", str))   # True
print(isinstance(42, int))        # True
print(isinstance(42.0, float))    # True

# === 精确计算：float 有精度问题 ===
# ⭐⭐ 常用 —— 浮点误差：0.1 + 0.2 != 0.3，不能直接判断相等
# Java: 同样问题，需要用 BigDecimal
print(0.1 + 0.2)       # 0.30000000000000004

# ⭐⭐ 常用 —— decimal.Decimal 精确计算（金额场景必用）
# Python 自带 decimal 模块 → Java BigDecimal
d1 = Decimal("0.1")
d2 = Decimal("0.2")
print(d1 + d2)          # 0.3（精确）

# === 类型小结 ===
# ⭐ 了解 —— Java 与 Python 类型对照速查表
# Java          → Python
# int/long      → int      （任意精度）
# float/double  → float
# char          → str（长度 1 的字符串）
# boolean       → bool（大写 True/False）
# null          → None
# BigDecimal    → decimal.Decimal
# BigInteger    → int

print("=== 02 数据类型 结束 ===")
