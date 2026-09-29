"""
===== 第9课：文件 I/O =====
对标 Java 的 FileInputStream / BufferedReader / Files 工具类
"""

import os
from pathlib import Path

# ==================== 读取文件 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# 创建演示文件
with open("demo.txt", "w", encoding="utf-8") as f:
    f.write("第一行\n第二行\n第三行\n")

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# === 方式1：with + read（推荐，≈ Java try-with-resources）===
# Java: try (BufferedReader br = new BufferedReader(new FileReader("demo.txt"))) { ... }
with open("demo.txt", "r", encoding="utf-8") as f:
    content = f.read()           # 读取全部
    print(content)

# ⭐⭐ 常用 —— 经常用
# === 逐行读取（≈ Java 的 readLine）===
with open("demo.txt", "r", encoding="utf-8") as f:
    for line in f:               # 直接迭代文件对象
        print(line, end="")      # line 已包含换行符

# ⭐⭐ 常用 —— 经常用
# === readlines → Java Files.readAllLines ===
# Java: List<String> lines = Files.readAllLines(Paths.get("demo.txt"));
with open("demo.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()        # 返回 list
    print(lines)

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# ==================== 写入文件 ====================
# Java: Files.write(Paths.get("out.txt"), content.getBytes());
with open("out.txt", "w", encoding="utf-8") as f:
    f.write("Hello Python\n")    # 覆盖写
    f.writelines(["a\n", "b\n", "c\n"])

# ⭐⭐ 常用 —— 经常用
# 追加写入（Java 的 StandardOpenOption.APPEND）
with open("out.txt", "a", encoding="utf-8") as f:
    f.write("追加行\n")

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# ==================== with 语句（try-with-resources）====================
# Java: try (Resource r = new Resource()) { ... }
# Python 的 with 自动调用 __enter__ 和 __exit__（close 在 __exit__ 中）
# 不限于文件，也用于锁、数据库连接等

# ==================== pathlib（Python 3.4+，推荐）====================
# 比 os.path 更现代，类似 Java NIO 的 Path

# ⭐⭐ 常用 —— 经常用
# Java: Path path = Paths.get("/usr/local", "demo.txt");
p = Path("/usr/local/demo.txt")
print(p.name)                    # demo.txt（getFileName()）
print(p.stem)                    # demo（无后缀文件名）
print(p.suffix)                  # .txt
print(p.parent)                  # /usr/local（getParent()）

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# 路径拼接（Java: Paths.get(parent, child)）
config = Path.home() / ".config" / "app"  # 用 / 拼接！
print(config)

# ⭐⭐ 常用 —— 经常用
# === 常用操作 ===
# 检查文件是否存在
if Path("demo.txt").exists():    # Java: Files.exists(path)
    print("文件存在")

# 创建目录
Path("test_dir/sub_dir").mkdir(parents=True, exist_ok=True)  # Java: Files.createDirectories()

# ⭐ 了解 —— 用到再查
# 列出目录
for f in Path(".").iterdir():    # Java: Files.list(path)
    print(f.name)

# ⭐ 了解 —— 用到再查
# === os.path 传统方式（了解即可） ===
print(os.path.exists("demo.txt"))
print(os.path.getsize("demo.txt"))

# ⭐ 了解 —— 用到再查
# ==================== 二进制文件 ====================
# 对比 Java 的 FileInputStream/FileOutputStream
with open("demo.bin", "wb") as f:    # wb = write binary
    f.write(b"\x00\x01\x02\x03")     # b 前缀 = 字节串

with open("demo.bin", "rb") as f:    # rb = read binary
    data = f.read()
    print(list(data))                # [0, 1, 2, 3]

# ==================== JSON 读写（对比 Jackson/Gson）====================
import json

data = {"name": "Alice", "scores": [90, 85, 95]}

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# 写入 JSON
# Java: objectMapper.writeValue(new File("data.json"), data);
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# 读取 JSON
# Java: Data data = objectMapper.readValue(new File("data.json"), Data.class);
with open("data.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)
    print(loaded["name"])          # Alice
    print(loaded["scores"])        # [90, 85, 95]

# ⭐ 了解 —— 用到再查
# 清理
import shutil
shutil.rmtree("test_dir", ignore_errors=True)
Path("demo.txt").unlink(missing_ok=True)      # 删除文件
Path("out.txt").unlink(missing_ok=True)
Path("demo.bin").unlink(missing_ok=True)
Path("data.json").unlink(missing_ok=True)

print("=== 09 文件 I/O 结束 ===")
