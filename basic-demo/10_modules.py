"""
===== 第10课：模块与包 =====
对标 Java 的 import / package
"""

# ==================== 导入（import = Java 的 import）====================

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# 方式1：导入整个模块（Java: import java.util.*;
import math
print(math.sqrt(16))          # 4.0
print(math.pi)                # 3.14159...

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# 方式2：导入特定内容（Java: import java.util.List;）
from math import sqrt, pi
print(sqrt(25))               # 5.0

# ⭐⭐ 常用 —— 经常用
# 方式3：别名（Java: 无直接对应）
import datetime as dt          # 起别名
print(dt.datetime.now())

# ⭐ 了解 —— 用到再查
# 方式4：导入所有（不推荐，命名冲突风险）
# from math import *

# ⭐ 了解 —— 用到再查
# ==================== 模块搜索路径 ====================
# Java: classpath 找 .class 文件
# Python: sys.path 找 .py 文件
import sys
print("Python 搜索路径:")
for p in sys.path:
    print(f"  {p}")

# ⭐⭐ 常用 —— 经常用
# ==================== __name__ 和 __main__ ====================
# 关键区别：模块被导入 vs 直接执行
# - 直接运行: __name__ = "__main__"
# - 被导入: __name__ = 模块名（如 "math"）
print(f"当前模块名: {__name__}")

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# 标准入口模式（对标 Java 的 main 方法）
def main():
    print("这是程序入口")

if __name__ == "__main__":
    main()

# ⭐⭐ 常用 —— 经常用
# ==================== 包（package）= 文件夹 ====================
"""
Java:
    package com.example.demo;
    import com.example.demo.Helper;

Python（更简单）：
    # 目录结构：
    # my_package/
    #   __init__.py     ← 标志这是个包（Java 不需要，但 Python 需要）
    #   module_a.py
    #   sub_package/
    #       __init__.py
    #       module_b.py

    # 导入方式：
    # import my_package.module_a
    # from my_package.sub_package import module_b

📌 创建包只需新建目录加 __init__.py 文件
   __init__.py 在包被导入时执行（类似 Java 的 static 初始化块）
"""

# ⭐⭐ 常用 —— 经常用
# ==================== 第三方包安装（对比 Maven/Gradle）====================
"""
Java (Maven)            Python (pip)
------------------------------
pom.xml                  requirements.txt
mvn install             pip install
mvn compile             python -m compileall
mvn test                pytest
mvn package             pip wheel

pip install requests       # 安装包（= mvn install）
pip list                   # 列出已安装（= mvn dependency:tree）
pip freeze > requirements.txt  # 导出依赖（= mvn dependency:tree > pom.xml）

用法示例：
import requests
resp = requests.get("https://api.github.com")
print(resp.status_code)
"""

# ⭐ 了解 —— 用到再查
# ==================== 创建临时模块演示 ====================
# 演示：创建并使用自定义模块

# 创建 my_utils.py
utils_code = """
# my_utils.py — 自定义工具模块
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

VERSION = "1.0.0"
"""

with open("my_utils.py", "w", encoding="utf-8") as f:
    f.write(utils_code)

# ⭐⭐ 常用 —— 经常用
import my_utils
print(my_utils.add(10, 5))         # 15
print(my_utils.VERSION)            # 1.0.0

# 也可以只导入特定函数
from my_utils import subtract
print(subtract(10, 5))             # 5

# ⭐ 了解 —— 用到再查
# 清理
import os
os.remove("my_utils.py")
# 删除缓存
import shutil
shutil.rmtree("__pycache__", ignore_errors=True)

print("=== 10 模块与包 结束 ===")
