"""
===== 第3课：字符串 =====
对标 Java 的 String/StringBuilder/StringBuffer
"""

# Python 字符串就是 str 类型，不可变（= Java String）
# ⭐⭐ 常用 —— 单引号与双引号等价，三引号可以跨行
# 三种引号
s1 = '单引号'              # Java 用双引号，Python 单双皆可
s2 = "双引号"
s3 = """三引号               # Java 没有，支持多行
可以换行
支持多行文本"""

# === 格式化（对比 Java） ===
name = "Tom"
age = 25
# ⭐⭐⭐ 必会 —— f-string：日常拼接与格式化的首选写法
# f-string（Python 3.6+，推荐）≈ Java 的 String.format / 文本块
# Java: String msg = String.format("我叫%s，今年%d岁", name, age);
msg = f"我叫{name}，今年{age}岁"
print(msg)

# ⭐ 了解 —— str.format()，老项目常见，新代码统一用 f-string
# format() ≈ Java 的 String.format()
msg2 = "我叫{}，今年{}岁".format(name, age)
print(msg2)

# ⭐ 了解 —— % 格式化，最古老的写法，维护老代码时才会遇到
# % 格式化（旧风格，了解即可）
msg3 = "我叫%s，今年%d岁" % (name, age)
print(msg3)

# === 常用方法 ===
# ⭐⭐⭐ 必会 —— len() 是内置函数；索引从 0 开始，负数表示从右往左
# Java: "hello".length(), "hello".charAt(0), "hello".substring(1, 3)
text = "Hello Python"
print(len(text))            # 12（len() 是函数，不是方法）
print(text[0])              # H（索引 = Java 的 charAt(0)）
print(text[-1])             # n（负数索引 = 从右往左！）
# ⭐⭐⭐ 必会 —— 切片 text[起:止]，左闭右开
print(text[0:5])            # Hello（切片 = Java 的 substring(0, 5)）
print(text[6:])             # Python（从索引 6 到末尾）
print(text[:5])             # Hello（从头到索引 5）

# 大小写
# ⭐⭐ 常用 —— 大小写转换，返回新字符串
print(text.upper())         # HELLO PYTHON
print(text.lower())         # hello python

# 判断
# ⭐⭐ 常用 —— 前后缀判断，比正则直观
print(text.startswith("He"))  # True
print(text.endswith("on"))    # True
# ⭐⭐ 常用 —— find() 查找子串位置，找不到返回 -1
print(text.find("Py"))        # 6（= Java indexOf，找不到返回 -1）
# ⭐⭐⭐ 必会 —— replace() 替换，返回新字符串（原串不可变）
print(text.replace("Python", "Java"))  # Hello Java

# === 拼接 ===
# ⭐⭐ 常用 —— join() 拼接可迭代对象，比循环里用 + 高效
# Java: String result = a + b + c; 或 StringBuilder
parts = ["a", "b", "c"]
result = "-".join(parts)     # a-b-c（Java 8+ 的 String.join）
print(result)

# 拆分
# ⭐⭐⭐ 必会 —— split() 按分隔符拆成列表（= Java String.split）
csv = "a,b,c"
items = csv.split(",")       # ['a', 'b', 'c']（String.split）
print(items)

# === 原始字符串（Java 没有） ===
# ⭐ 了解 —— r"" 原始字符串，反斜杠不转义（写路径、正则时用）
# 反斜杠不会被转义
path = r"C:\Users\name"      # 加 r 前缀
print(path)                  # C:\Users\name（不会把 \U 当转义）

# === 多行字符串 ===
# ⭐⭐ 常用 —— 三引号多行字符串（写 SQL、模板、长文本时用）
multiline = """
SELECT *
FROM users
WHERE age > 18
"""
print(multiline)

print("=== 03 字符串 结束 ===")
