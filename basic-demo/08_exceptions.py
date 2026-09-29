"""
===== 第8课：异常处理 =====
对标 Java 的 try-catch-finally / throws
"""

print('⚠️ 本课会故意触发若干异常用于教学演示，它们都会被 try/except 捕获，控制台出现 Error / Exception 字样属正常现象，脚本退出码为 0\n')

# ==================== try-except（Java 的 try-catch）====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: try { ... } catch (Exception e) { ... }
try:
    num = int("不是数字")      # 会抛 ValueError
    result = 10 / 0             # 会抛 ZeroDivisionError
except ValueError:
    print("数值转换失败")
except ZeroDivisionError as e:  # as e = catch(Exception e)
    print(f"除零错误: {e}")

# === 捕获多个异常 ===
# ⭐⭐ 常用 —— 经常用
# Java: catch (IOException | SQLException e) { ... }
try:
    x = int("abc")
except (ValueError, TypeError) as e:
    print(f"捕获到: {type(e).__name__}")

# === 捕获所有异常（慎用） ===
# ⭐⭐ 常用 —— 经常用
# Java: catch (Exception e) { ... }
def risky_operation():
    """模拟一个未预料的错误：把 None 当对象用"""
    data = None
    return data.attr            # 抛 AttributeError

try:
    risky_operation()
except Exception as e:          # Exception 捕获所有（子类都在内）
    print(f"未知错误: {type(e).__name__}: {e}")

# ==================== try-except-else-finally ====================
# ⭐⭐ 常用 —— 经常用
# Java: try { ... } catch { ... } finally { ... }
try:
    result = 100 / 5
except ZeroDivisionError:
    print("不能除零")
# ⭐ 了解 —— 用到再查
else:                          # Java 没有！没有异常时执行
    print(f"计算成功: {result}")
finally:                       # 同 Java
    print("总是执行")

# ==================== 抛异常（throw）====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: throw new IllegalArgumentException("msg");
def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("除数不能为 0")   # raise = Java throw
    return a / b

try:
    divide(10, 0)
except ValueError as e:
    print(e)

# ==================== 自定义异常 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: public class MyException extends RuntimeException { ... }
class BusinessException(Exception):    # 继承 Exception
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")

def withdraw(amount: float):
    if amount > 10000:
        raise BusinessException(1001, "超过单笔限额")

try:
    withdraw(20000)
except BusinessException as e:
    print(f"业务异常: code={e.code}, msg={e.message}")

# ==================== try-with-resources 的 Python 方式 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: try (FileInputStream fis = new FileInputStream("file.txt")) { ... }
# Python 用 with 语句
print("详见 09_file_io.py 的 with 语句")

# ==================== 异常链 ====================
# ⭐⭐ 常用 —— 经常用
# Java: catch (Exception e) { throw new RuntimeException("包裹", e); }
def read_file():
    try:
        open("不存在的文件.txt")
    except FileNotFoundError as e:
        raise RuntimeError("读取失败") from e  # from = 异常链

# ==================== 断言（assert）====================
# ⭐ 了解 —— 用到再查
# Java: assert age >= 0 : "年龄不能为负";
age = -1
# assert age >= 0, "年龄不能为负"    # 条件为 False 时抛 AssertionError

# ==================== 常用内置异常 ====================
# ⭐⭐ 常用 —— 经常用
# ValueError     → 参数值不合法  （≈ IllegalArgumentException）
# TypeError      → 类型不匹配     （≈ ClassCastException）
# IndexError     → 索引越界       （≈ ArrayIndexOutOfBoundsException）
# KeyError       → 字典 key 不存在（≈ NoSuchElementException）
# FileNotFoundError → 文件找不到  （≈ FileNotFoundException）
# ZeroDivisionError → 除零        （≈ ArithmeticException）
# AttributeError → 属性不存在     （≈ NullPointerException 部分场景）

print("=== 08 异常处理 结束 ===")
