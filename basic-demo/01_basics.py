"""
===== 第1课：基础语法 =====
对标 Java 的核心差异：动态类型、缩进、无分号、无 main 方法
"""

# ⭐⭐⭐ 必会 —— print 输出；脚本从第一行开始执行
# Java: public class Hello { public static void main(String[] args) { ... } }
# Python：脚本从第一行开始执行，无需类包裹
print("Hello Python!")

# === 变量声明（无类型声明） ===
# ⭐⭐⭐ 必会 —— 直接赋值即可，不需要写类型声明
# Java: String name = "Alice";
name = "Alice"           # 自动推断为 str
age = 25                 # 自动推断为 int
height = 1.75            # 自动推断为 float
is_student = True        # 注意大写 T/F，Java 是小写 true/false


# ⭐⭐ 常用 —— print 一次输出多个值，逗号分隔并自动加空格
print(name, age, height, is_student)

# === 动态类型 ≈ Java 的 Object ===
# ⭐⭐ 常用 —— 动态类型：变量只是标签，随时可以指向另一种类型
# Java: Object x = "hello";  x = 42;   // 需要装箱
x = "hello"
x = 42  # 合法，因为变量只是标签

# === 缩进 = 作用域（无 {}） ===
# ⭐⭐⭐ 必会 —— 用缩进划分代码块，if/else 行尾必须有冒号，没有大括号
# Java: if (true) { System.out.println("ok"); }
# ⚠️ Python 语句结尾不写分号（写了不报错，但属反模式，Java 开发者最容易带过来）
score = 75
if score >= 60:              # 条件表达式后必须有冒号
    print("及格")            # 缩进 4 空格 = Java 的 {}
    print("同一缩进级别 = 同一代码块")
else:
    print("不及格")

# === 无需 main 方法，但推荐写法 ===
# 这个 if 是 Python 惯例：被导入时不执行，直接运行时才执行
# ⭐⭐⭐ 必会 —— def 定义函数
def main():
    print("这是 main 函数，类似 Java 的 public static void main")

# ⭐⭐⭐ 必会 —— 程序入口惯例：直接运行才执行，被 import 时不执行
if __name__ == "__main__":
    main()

# === 注释 ===
# ⭐⭐ 常用 —— 单行注释用 #
# 单行注释用 #
# ⭐ 了解 —— 三引号字符串常被当作多行注释（本质仍是字符串）
""" 多行注释用三个引号（本质是字符串） """

# === 控制台输入 ===
# ⭐⭐ 常用 —— input() 读取一行输入，返回值永远是 str
# Java: Scanner sc = new Scanner(System.in); String s = sc.nextLine();
user_input = input("输入你的名字: ")
print("你好,", user_input)

print("=== 01 基础语法 结束 ===")
