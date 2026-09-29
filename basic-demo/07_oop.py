"""
===== 第7课：面向对象 =====
对标 Java 的 class/interface/extends
"""

# ==================== 定义类 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: public class Dog { private String name; ... }
class Dog:
    """狗类"""

    # ⭐⭐ 常用 —— 经常用
    # 类变量（= Java static field）
    species = "Canis familiaris"

    # ⭐⭐⭐ 必会 —— 天天写，不用查文档
    # 构造方法（= Java 构造函数）
    # Java: public Dog(String name, int age) { this.name = name; }
    def __init__(self, name: str, age: int):
        self.name = name       # 实例变量（Java field）
        self.age = age
        # ⭐ 了解 —— 用到再查
        self._secret = "秘密"   # 单下划线 = 约定内部使用（非强制）
        self.__private = "私有" # 双下划线 = 名称修饰（name mangling）

    # ⭐⭐⭐ 必会 —— 天天写，不用查文档
    # 实例方法（= Java 普通方法）
    # Java: public void bark() { ... }
    def bark(self):
        """第一个参数 self = Java 的 this"""
        print(f"{self.name} 在叫: 汪汪！")

    # ⭐⭐ 常用 —— 经常用
    # Java: @Override public String toString() { ... }
    def __str__(self) -> str:
        return f"Dog(name={self.name}, age={self.age})"

    def __repr__(self) -> str:
        return self.__str__()

# === 创建对象 ===
# Java: Dog dog = new Dog("旺财", 3);
dog = Dog("旺财", 3)
print(dog)                 # 调用 __str__
dog.bark()

# === 访问属性 ===
# ⭐⭐ 常用 —— 经常用
print(dog.name)            # 直接访问，不需要 getter/setter
dog.name = "大黄"          # 直接修改
print(Dog.species)         # 类变量

# === 访问修饰符 ===
print(dog._secret)         # 能访问，但约定别动
# print(dog.__private)     # ❌ 报错
print(dog._Dog__private)   # 能绕过（但别这么干）

# ==================== 继承 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: public class Puppy extends Dog { ... }
class Puppy(Dog):          # 父类写在括号里
    # ⭐⭐ 常用 —— 经常用
    def __init__(self, name: str, age: int, toy: str):
        super().__init__(name, age)   # Java: super(name, age)
        self.toy = toy

    # ⭐⭐⭐ 必会 —— 天天写，不用查文档
    # 重写（override）
    def bark(self):
        super().bark()                # 调用父类方法
        print(f"{self.name} 小声叫: 呜~")

    # Java 的 @Override 是注解，Python 靠 duck typing

puppy = Puppy("小黄", 1, "球")
puppy.bark()

# === 类型判断 ===
# ⭐⭐ 常用 —— 经常用
print(isinstance(puppy, Puppy))   # True
print(isinstance(puppy, Dog))     # True（继承链）
print(isinstance(puppy, object))  # True（万物皆对象）

# ==================== @property = getter/setter 的 Python 方式 ====================
class Student:
    def __init__(self, name: str):
        self._name = name
        self._score = 0

    # ⭐⭐ 常用 —— 经常用
    # Java: public String getName() { return name; }
    @property
    def score(self):
        return self._score

    # ⭐⭐ 常用 —— 经常用
    # Java: public void setScore(int score) { this.score = score; }
    @score.setter
    def score(self, value):
        if not (0 <= value <= 100):
            raise ValueError("分数必须在 0-100 之间")
        self._score = value

s = Student("Alice")
s.score = 85               # 调用 setter，像属性一样赋值
print(s.score)             # 调用 getter，像属性一样取值
# s.score = 200            # ❌ ValueError

# ==================== 特殊方法（dunder methods，对标 Java 的方法）====================
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # ⭐ 了解 —— 用到再查
    def __add__(self, other):      # Java: Vector add(Vector other)
        return Vector(self.x + other.x, self.y + other.y)

    def __eq__(self, other):       # Java: @Override equals()
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

v1 = Vector(1, 2)
v2 = Vector(3, 4)
print(v1 + v2)                     # Vector(4, 6)
print(v1 == Vector(1, 2))          # True

# ==================== 抽象类（对标 abstract class）====================
# ⭐⭐ 常用 —— 经常用
from abc import ABC, abstractmethod

# Java: public abstract class Animal { public abstract void sound(); }
class Animal(ABC):
    @abstractmethod
    def sound(self): ...

class Cat(Animal):
    def sound(self):
        print("喵")

cat = Cat()
cat.sound()

# ==================== 接口（Python 用抽象类代替）====================
# Java: public interface Flyable { void fly(); }
# Python 没有 interface 关键字，用 ABC 或者 duck typing
class Flyable(ABC):
    @abstractmethod
    def fly(self): ...

class Bird(Flyable):
    def fly(self):
        print("飞")

# Python 倡导 duck typing："如果它走路像鸭子，叫像鸭子，就是鸭子"

# ==================== 总结对比 ====================
# Java                    → Python
# public class            → class
# private field           → _field（约定）
# this                    → self
# constructor             → __init__
# toString()              → __str__
# equals()                → __eq__
# implements Interface    → class Foo(InterfaceABC)
# extends                 → class Child(Parent)
# @Override               → 直接重写
# @property               → @property
# 接口                     → ABC + @abstractmethod

print("=== 07 面向对象 结束 ===")
