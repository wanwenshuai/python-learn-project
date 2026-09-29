"""
===== 第5课：控制流 =====
对标 Java 的 if/for/while/switch
"""

# ==================== if-elif-else（Java 的 if-else if-else）====================
score = 85

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: if (score >= 90) { ... } else if (score >= 80) { ... } else { ... }
if score >= 90:
    grade = "A"
elif score >= 80:              # 注意是 elif，不是 else if
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "D"

print(f"等级: {grade}")

# === 三目运算符 ===
# ⭐⭐ 常用 —— 经常用
# Java: String result = (age >= 18) ? "成年" : "未成年";
age = 20
result = "成年" if age >= 18 else "未成年"
print(result)

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# === 真值判断（Python 特色） ===
# 以下值被视为 False：False, None, 0, 0.0, "", [], (), {}, set()
# Java 中空引用会 NPE，这里更宽松
name = ""
if not name:         # "" 是假，等价于 Java 的 name.isEmpty()
    print("名字为空")

items = []
if not items:        # [] 是假
    print("列表为空")

# ==================== for 循环 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: for (int i = 0; i < 5; i++) { ... }
# Python 用 range()
for i in range(5):           # 0, 1, 2, 3, 4
    print(i, end=" ")
print()

for i in range(2, 6):        # 2, 3, 4, 5（开始, 结束）
    print(i, end=" ")
print()

for i in range(0, 10, 2):    # 0, 2, 4, 6, 8（步长）
    print(i, end=" ")
print()

# 遍历集合
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: for (String fruit : fruits) { ... }
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# 带索引遍历
# ⭐⭐ 常用 —— 经常用
# Java: for (int i = 0; i < fruits.size(); i++) { ... }
for i, fruit in enumerate(fruits):   # enumerate 返回 (索引, 值) 元组
    print(f"{i}: {fruit}")

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# 遍历字典
student = {"name": "Alice", "age": 25}
for key in student:                 # 遍历 key
    print(key)
for value in student.values():       # 遍历 value
    print(value)
for key, value in student.items():   # 遍历 key-value
    print(f"{key}={value}")

# ==================== while 循环（同 Java）====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
count = 0
while count < 3:
    print(f"count = {count}")
    count += 1

# ==================== break / continue（同 Java）====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
for i in range(10):
    if i == 3:
        continue         # 跳过
    if i == 7:
        break            # 终止
    print(i, end=" ")    # 0 1 2 4 5 6

print()

# ==================== for-else（Java 没有！）====================
# ⭐ 了解 —— 用到再查
# for 正常结束（未被 break）时执行 else
for n in range(2, 10):
    for x in range(2, n):
        if n % x == 0:
            break
    else:               # 注意：属于内层 for，不是 if
        print(f"{n} 是质数")

# ==================== match-case（Python 3.10+，对标 Java 17+ switch）====================
# ⭐⭐ 常用 —— 经常用
# Java 17: switch (x) { case 1 -> ...; case 2 -> ...; default -> ...; }
status_code = 404

match status_code:
    case 200:
        print("OK")
    case 404:
        print("Not Found")
    case 500:
        print("Server Error")
    case _:              # 默认分支
        print("Unknown")

# ⭐ 了解 —— 用到再查
# 模式匹配（Java 没有）
point = (0, 0)
match point:
    case (0, 0):
        print("原点")
    case (x, 0):
        print(f"X 轴, x={x}")
    case (0, y):
        print(f"Y 轴, y={y}")
    case (x, y):
        print(f"普通点 x={x}, y={y}")

print("=== 05 控制流 结束 ===")
