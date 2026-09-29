"""
===== 第4课：集合（容器） =====
对标 Java 的 List/Set/Map
"""

# Python 有 4 种内置容器类型

# ==================== 1. list（列表）= Java 的 ArrayList ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: List<String> list = new ArrayList<>();
fruits = ["apple", "banana", "cherry"]
print(fruits)               # ['apple', 'banana', 'cherry']

# 泛型？Python 不需要，可以混装
mixed = [1, "hello", 3.14, True]

# 增删改
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
fruits.append("orange")     # add()       → ['apple', 'banana', 'cherry', 'orange']
fruits.insert(1, "grape")   # add(index, e)
fruits.remove("banana")     # remove(Object)
popped = fruits.pop()       # remove(index) 默认最后一个
print(popped)               # orange
print(fruits[0])            # 索引 get(0)
print(fruits[-1])           # 最后一个

# ⭐⭐ 常用 —— 经常用
# 切片（Python 独有）
nums = [0, 1, 2, 3, 4, 5]
print(nums[1:4])            # [1, 2, 3]
print(nums[::2])            # [0, 2, 4]（步长 2）
print(nums[::-1])           # [5, 4, 3, 2, 1, 0]（反转）

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# 列表推导式 ≈ Java 8 Stream map
# Java: list.stream().map(x -> x * 2).collect(toList())
squares = [x * x for x in range(10)]
print(squares)              # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# ⭐⭐ 常用 —— 经常用
# 带过滤的推导式 ≈ Java 8 filter
# Java: list.stream().filter(x -> x % 2 == 0).collect(toList())
evens = [x for x in range(10) if x % 2 == 0]
print(evens)                # [0, 2, 4, 6, 8]

# ==================== 2. tuple（元组）= 不可变的 List ====================
# ⭐⭐ 常用 —— 经常用
# Java：无直接对应，类似 List.of(...) 不可变列表
# 一旦创建不能修改（final 语义）
point = (3, 4)
print(point[0])             # 3
# point[0] = 99            # ❌ 编译时错误（实际上运行时报错）

# ⭐⭐ 常用 —— 经常用
# 元组解包（Python 特色）
x, y = point               # 类似 Java 没有，但很方便
print(f"坐标: {x}, {y}")

# ⭐⭐ 常用 —— 经常用
# 方法返回多值 = 本质返回元组
def get_user():
    return "Alice", 25      # 自动打包成元组

name, age = get_user()     # 解包
print(name, age)

# ==================== 3. set（集合）= Java 的 HashSet ====================
# ⭐⭐ 常用 —— 经常用
# Java: Set<String> set = new HashSet<>();
unique = {1, 2, 3, 2, 1}
print(unique)               # {1, 2, 3}（自动去重）

# ⭐ 了解 —— 用到再查
unique.add(4)
unique.discard(2)           # remove 但不存在不抛异常

# ⭐⭐ 常用 —— 经常用
# 集合运算（Java 需手动实现或 Guava）
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}
print(a & b)                # 交集 → {3, 4}
print(a | b)                # 并集 → {1, 2, 3, 4, 5, 6}
print(a - b)                # 差集 → {1, 2}
print(a ^ b)                # 对称差 → {1, 2, 5, 6}

# ==================== 4. dict（字典）= Java 的 HashMap ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: Map<String, Integer> map = new HashMap<>();
student = {"name": "Alice", "age": 25, "score": 90}
print(student["name"])      # Alice（Java 的 map.get("name")）

# 增删改
# ⭐ 了解 —— 用到再查
student["grade"] = "A"      # put
del student["score"]        # remove
print(student)

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# 安全获取（不抛异常）
# Java: map.getOrDefault("xxx", "默认值")
print(student.get("xxx", "默认值"))  # 默认值

# 遍历
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
for key, value in student.items():  # Java: for (Map.Entry entry : map.entrySet())
    print(f"{key} = {value}")

# ⭐⭐ 常用 —— 经常用
# 字典推导式
squares_dict = {x: x * x for x in range(5)}
print(squares_dict)          # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# ==================== 对比总结 ====================
# Java            → Python
# ArrayList       → list
# LinkedList      → list（collections.deque 更优）
# HashSet         → set
# LinkedHashSet   → dict（只有 dict 有插入顺序保证；set 是 hash 定序，不保序）
# HashMap         → dict（Python 3.7+ 保证插入顺序，比 HashMap 更强）
# TreeMap         → 需第三方 sortedcontainers
# TreeMap         → dict（无内置，用 sortedcontainers 库）
# List.of()       → tuple
# Arrays.asList() → list

print("=== 04 集合 结束 ===")
