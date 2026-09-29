"""
===== 第19课：正则表达式 =====
对标 Java 的 Pattern / Matcher
"""

print('⚠️ 本课会故意触发若干异常用于教学演示，它们都会被 try/except 捕获，控制台出现 Error / Exception 字样属正常现象，脚本退出码为 0\n')

import re

# ⚠️⚠️⚠️ 开篇最重要的一条铁律，先看这里，能省你半天排查时间：
# Python 的 re.match  ≠  Java 的 Matcher.matches()
# Python 的 re.match  ≈  Java 的 Matcher.lookingAt()（只从开头匹配，不要求匹配到结尾）
# Python 的 re.fullmatch 才是 Java 的 Matcher.matches()
# Python 的 re.search ≈  Java 的 Matcher.find()
#
# 另一个铁律：Python 正则一律写原始字符串 r"..."。
# Java 里写 "\\d+"（字符串转义 + 正则转义双层），Python 里写 r"\d+"（一层，所见即所得）。


# ==================== 一、三个匹配方法的区别（最容易搞错）====================

# ⭐⭐⭐ 必会 —— re.match：只从「开头」匹配，不要求匹配到结尾
# Java: Pattern.compile("\\d+").matcher("123abc").lookingAt()
# ⚠️ 注意：不是完全匹配！只要开头能匹配上就返回 Match 对象，后面的内容它根本不管
m1 = re.match(r"\d+", "123abc")
print(m1)                       # <re.Match object; span=(0, 3), match='123'>
print(m1.group())               # 123（只吃掉了开头的 123，abc 被无视）

# 开头不匹配直接返回 None
print(re.match(r"\d+", "abc123"))       # None
# Java 开发者最容易犯的错：把上面这行当成「校验字符串是不是纯数字」
# 结果 "abc123" 返回 None，就以为没事；换成 "123abc" 就返回 Match 了 —— 校验直接漏判

# ⭐⭐⭐ 必会 —— re.fullmatch：整个字符串必须完全匹配（这才是 Java 的 matches()）
# Java: Pattern.compile("\\d+").matcher("123abc").matches()
print(re.fullmatch(r"\d+", "123abc"))   # None ← 有 abc 尾巴，不算完全匹配
print(re.fullmatch(r"\d+", "123"))      # <re.Match object; span=(0, 3), match='123'>
# 💡 结论：做「格式校验」（手机号、身份证、邮箱）永远用 fullmatch，不要用 match

# ⭐⭐⭐ 必会 —— re.search：全串扫描，找第一个匹配（≈ Java 的 find()）
# Java: Pattern.compile("\\d+").matcher("abc123def456").find()
m3 = re.search(r"\d+", "abc123def456")
print(m3)                       # <re.Match object; span=(3, 6), match='123'>
print(m3.group())               # 123（只返回第一个，不是全部）

# 三者用同一个模式、同一个字符串的正面对比
pattern = r"\d+"
text = "abc123def"
print(re.match(pattern, text))          # None（开头是 a，match 直接放弃）
print(re.fullmatch(pattern, text))      # None（整串不是纯数字）
print(re.search(pattern, text))         # <re.Match object; span=(3, 6), match='123'>

# 换成以数字开头的字符串，match 就"活"了
text2 = "123abc"
print(re.match(pattern, text2))         # <re.Match object; span=(0, 3), match='123'>
print(re.fullmatch(pattern, text2))     # None（仍然要求整串匹配）

# 一句话对照表：
#   Python              Java                       语义
#   re.match(p, s)      matcher(s).lookingAt()     开头锚定，不要求结尾
#   re.fullmatch(p, s)  matcher(s).matches()       整串完全匹配
#   re.search(p, s)     matcher(s).find()          任意位置找第一个

# 正则里的 ^ 和 \b 在 match 里是多余的（match 自带开头锚定），但写了也不报错
print(re.match(r"^\d+", "123abc"))      # <re.Match object; span=(0, 3), match='123'>


# ==================== 二、匹配对象 Match ====================

# ⭐⭐⭐ 必会 —— group 系列
# Java: Matcher.group() / group(1) / groupCount()
m = re.search(r"(\d+)-(\d+)", "order 2024-01")
print(m.group())                # 2024-01（group() == group(0)，整个匹配）
print(m.group(0))               # 2024-01
print(m.group(1))               # 2024（第 1 个分组）
print(m.group(2))               # 01（第 2 个分组）
print(m.groups())               # ('2024', '01')（所有分组组成的元组，不含 group(0)）
# Java: m.groupCount() 返回 2
print(len(m.groups()))          # 2

# ⭐⭐⭐ 必会 —— start / end / span（Java 没有直接等价物，要自己算）
# Java: m.start() / m.end() 是有的，Python 语义完全一致（左闭右开）
print(m.start())                # 6（匹配起始下标）
print(m.end())                  # 13（匹配结束下标，不含）
print(m.span())                 # (6, 13)
print("order 2024-01"[6:13])    # 2024-01（切片拿回原文）

# 位置信息最实用的场景：只替换匹配到的那一段，原文其它部分原样保留
price = "价格 100 元"
m2 = re.search(r"\d+", price)
print(price[:m2.start()] + "99.9" + price[m2.end():])   # 价格 99.9 元
# 💡 这就是 re.sub 的底层原理（虽然实战当然直接写 re.sub）

# ⭐⭐⭐ 必会 —— 匹配失败返回 None，必须先判空
# Java 里 find() 失败返回 false，你只能先去 group() 才抛 IllegalStateException；
# Python 更直接：失败就是 None，你直接 .group() 会抛 AttributeError
none_match = re.match(r"\d+", "abc")
try:
    none_match.group()
except AttributeError as e:
    print(f"AttributeError: {e}")       # AttributeError: 'NoneType' object has no attribute 'group'

# 正确写法一：判 None
if none_match is not None:
    print(none_match.group())
else:
    print("没匹配上")                    # 没匹配上

# 正确写法二：用海象运算符（Python 3.8+，很常用的写法）
if found := re.search(r"\d+", "abc123"):
    print(found.group())                # 123

# 正确写法三：用 or 短路（只关心有没有，不关心内容时）
print(bool(re.search(r"\d+", "abc")))   # False


# ==================== 三、查找全部 ====================

# ⭐⭐⭐ 必会 —— re.findall：一次性返回所有匹配（字符串列表）
# Java: while (matcher.find()) { list.add(matcher.group()); }  —— 要写循环
# Java: Matcher.results() 才是等价物（Java 9+）
print(re.findall(r"\d+", "a1b22c333"))          # ['1', '22', '333']
print(re.findall(r"\d+", "没有数字"))            # []（没匹配返回空列表，不是 None）

# ⭐⭐⭐ 必会 —— 有分组时，findall 返回的是「分组元组」列表，不是整体匹配！
# 这是让无数人翻车的点：加了括号，返回值立刻变形
print(re.findall(r"(\d+)-(\d+)", "2024-01 2025-12"))    # [('2024', '01'), ('2025', '12')]
# 只写一个分组时，返回的是一维字符串列表（元组自动退化）
print(re.findall(r"(\d+)-", "2024-01 2025-12"))         # ['2024', '2025']
# 整体匹配反而丢了！要整体匹配又不想变形 → 用非捕获分组 (?:...)（见第四节）
print(re.findall(r"(?:\d+)-(\d+)", "2024-01 2025-12"))  # ['01', '12']

# ⭐⭐⭐ 必会 —— re.finditer：返回 Match 迭代器，能拿到位置信息（findall 拿不到）
# Java: while (matcher.find()) 循环，几乎是逐字对应
# Java: for (MatchResult mr : matcher.results().toList())
for it in re.finditer(r"\d+", "a1b22c333"):
    print(f"{it.group()} 在 [{it.start()}, {it.end()})")     # 三行：1 在 [1, 2) / 22 在 [3, 5) / 333 在 [6, 9)

# 用生成器表达式取出列表（等价于 findall，但要什么取什么，更灵活）
print([mi.group() for mi in re.finditer(r"\d+", "a1b22c333")])   # ['1', '22', '333']

# 💡 findall / finditer 怎么选：
#    只要匹配到的文本  → findall（一行搞定）
#    还要位置、还要分组字典 → finditer


# ==================== 四、分组 ====================

# ⭐⭐⭐ 必会 —— 普通分组 ()：既分组又捕获
# Java: Pattern.compile("(\\d{4})-(\\d{2})")
d = re.search(r"(\d{4})-(\d{2})-(\d{2})", "日期 2024-01-15")
print(d.group(1), d.group(2), d.group(3))       # 2024 01 15
print(d.groups())                               # ('2024', '01', '15')

# 分组嵌套时，编号按「左括号出现的顺序」数
nest = re.search(r"((\d{4})-(\d{2}))-(\d{2})", "2024-01-15")
print(nest.group(1))            # 2024-01（外层大分组）
print(nest.group(2))            # 2024（内层第 2 组）
print(nest.group(4))            # 15（内层第 4 组）

# ⭐⭐⭐ 必会 —— 非捕获分组 (?:...)：只要分组逻辑，不要编号
# Java: 也有 (?:...)，语法完全一致
# 什么时候用：① 只是给量词圈定范围，不想污染 group 编号
#             ② 不想让 findall 的结果因为分组而变成元组
print(re.findall(r"(?:ab)+", "ababab cd ab"))   # ['ababab', 'ab']（有括号但不捕获，结果不变形）
print(re.findall(r"(ab)+", "ababab cd ab"))     # ['ab', 'ab']（捕获了，结果只剩最后一轮）

# 实战：匹配 "http 或 https" 前缀，但不关心具体是哪个
urls = "http://a.com https://b.com ftp://c.com"
print(re.findall(r"(?:https?)://([\w.]+)", urls))    # ['a.com', 'b.com']
# 对比：如果写成 (https?)://([\w.]+)，结果会变成 [('http', 'a.com'), ('https', 'b.com')]

# ⭐⭐⭐ 必会 —— 命名分组 (?P<name>...)，Python 语法
# ⚠️ Java 是 (?<name>...)，Python 多一个 P= 前缀，别写串
# Java: Pattern.compile("(?<year>\\d{4})-(?<month>\\d{2})")
nd = re.search(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})", "2024-01-15")
print(nd.group("year"))         # 2024
print(nd.group("month"))        # 01
print(nd.group("day"))          # 15
# 命名分组同时也有编号，两种取法都行
print(nd.group(1))              # 2024
# Java: matcher.group("year")
print(nd.groupdict())           # {'year': '2024', 'month': '01', 'day': '15'}
# 命名 + 普通分组混用时，groupdict() 只含命名分组，groups() 含全部
mixed = re.search(r"(?P<a>\d)(\d)", "12")
print(mixed.groups())           # ('1', '2')
print(mixed.groupdict())        # {'a': '1'}

# 反向引用：在模式内部引用前面捕获到的内容
# Java: \\1
print(re.findall(r"(\w)\1", "aabbcdeff"))       # ['a', 'b', 'f']（重复出现的字符）
# 命名分组的反向引用用 (?P=name)，Java 是 \k<name>
print(re.findall(r"(?P<c>\w)(?P=c)", "aabbc"))   # ['a', 'b']


# ==================== 五、替换 ====================

# ⭐⭐⭐ 必会 —— re.sub(pattern, repl, string, count=)
# Java: matcher.replaceAll(replacement) / replaceFirst(replacement)
print(re.sub(r"\d+", "#", "a1b22c333"))             # a#b#c#
# count 限制替换次数（Java 要自己写循环或用 replaceFirst）
print(re.sub(r"\d+", "#", "a1b22c333", count=1))    # a#b22c333
print(re.sub(r"\d+", "#", "a1b22c333", count=2))    # a#b#c333

# ⭐⭐⭐ 必会 —— 反向引用 \1 \2 出现在「替换串」里
# Java: replaceAll("$2/$1") 用的是 $ 符号，Python 用 \ ，别写串
# Java: matcher.replaceAll("$3/$2/$1")
print(re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1", "2024-01-15"))    # 15/01/2024
# 命名分组的反向引用：\g<name>（注意是 \g<...>，不能用 \name，因为 \n 会被当成换行）
print(re.sub(r"(?P<y>\d{4})-(?P<m>\d{2})", r"\g<m>/\g<y>", "2024-01-15"))  # 01/2024-15

# ⭐⭐⭐ 必会 —— repl 传函数：接收 Match 对象，返回替换后的字符串
# Java: matcher.replaceAll(mr -> ...)  —— Java 9+ 才有，接收 MatchResult
def double_it(mt):
    """把匹配到的数字翻倍"""
    return str(int(mt.group()) * 2)

print(re.sub(r"\d+", double_it, "a1b2c3"))          # a2b4c6

# 函数替换的威力：能读分组、能做条件判断
def mask_phone(mt):
    """手机号中间四位打码"""
    return mt.group(1) + "****" + mt.group(2)

print(re.sub(r"(\d{3})\d{4}(\d{4})", mask_phone, "手机 13812345678"))   # 手机 138****5678

# 条件替换：只替换 > 100 的数字
def cap_num(mt):
    v = int(mt.group())
    return "#" if v > 100 else mt.group()

print(re.sub(r"\d+", cap_num, "a5b50c500"))         # a5b50c#

# ⭐⭐ 常用 —— re.subn：返回 (替换后的字符串, 替换次数)
# Java 没有直接等价物，要自己数
print(re.subn(r"\d+", "#", "a1b22c333"))            # ('a#b#c#', 3)
print(re.subn(r"\d+", "#", "abc"))                  # ('abc', 0)
result, n = re.subn(r"\d+", "#", "a1b22c333")
print(f"替换了 {n} 处")                              # 替换了 3 处


# ==================== 六、切分 ====================

# ⭐⭐⭐ 必会 —— re.split：按正则切分，能处理多个不同分隔符
# Java: String.split("[,;|\\s]+") —— Python 的 str.split 只能按固定串，没法多分隔符
# Java: pattern.split("a,b;c d")  —— re.split 与 Pattern.split 完全等价
print(re.split(r"[,;|\s]+", "a,b;c d"))             # ['a', 'b', 'c', 'd']
# 对比 str.split 的能力上限
print("a,b;c d".split(","))                         # ['a', 'b;c d']（只认逗号，其余原样保留）

# 常用写法：按空白切分（等价于 str.split() 无参，但正则能加限制）
print(re.split(r"\s+", "  hello   world  "))        # ['', 'hello', 'world', '']
print("  hello   world  ".split())                  # ['hello', 'world']（无参 str.split 更省心）

# ⭐⭐⭐ 必会 —— 带分组时，结果里会「包含分隔符」这是 Python 独有的特性
# Java 的 split 永远丢弃分隔符，Python 靠一个括号就把分隔符留在结果里
print(re.split(r"([,;])", "a,b;c"))                 # ['a', ',', 'b', ';', 'c']
# 原理：所有捕获分组的内容会被依次插入结果列表。不想要就写非捕获分组 (?:...)
print(re.split(r"(?:[,;])", "a,b;c"))               # ['a', 'b', 'c']

# 限制切分次数：maxsplit
print(re.split(r",", "a,b,c,d", maxsplit=2))        # ['a', 'b', 'c,d']

# 实用场景：切 URL 路径
print(re.split(r"[/]+", "/api/v1/users/"))          # ['', 'api', 'v1', 'users', '']


# ==================== 七、预编译与 flags ====================

# ⭐⭐⭐ 必会 —— re.compile 返回 Pattern 对象（与 Java 的 Pattern.compile 一一对应）
# Java: Pattern p = Pattern.compile("\\d+");
# Java: Matcher m = p.matcher(s);
pat = re.compile(r"\d+")
print(pat)                                      # re.compile('\\d+')
print(type(pat))                                # <class 're.Pattern'>
print(pat.findall("a1b22c333"))                 # ['1', '22', '333']
print(pat.search("a1b22c333").group())          # 1
print(pat.sub("#", "a1b22"))                    # a#b#
# 预编译对象还能反过来查看它自己的信息
print(pat.pattern)                              # \d+
print(pat.flags)                                # 32

# ⭐⭐⭐ 必会 —— 为什么要预编译
# re 模块内部有 LRU 缓存（默认缓存 512 个模式），所以 re.match(r"\d+", s) 并非每次都重新解析。
# 但在循环/热点方法里反复调用时：
#   ① 每次都要算缓存 key（模式串 + flags）并查字典，命中后还要查一次
#   ② 缓存被写满后会淘汰旧条目，模式一多就反复「解析 → 淘汰 → 再解析」
# 显式 compile 一次，循环里就只剩纯粹的匹配，省掉全部查找与淘汰开销。
# Java 里同样是这个结论：Pattern.compile 是重操作，绝不要写在循环体内。
pattern_hot = re.compile(r"\d{4}-\d{2}-\d{2}")

def count_lines_with_date(lines: list) -> int:
    """统计含有日期的行数（热点循环里复用同一个 Pattern 对象）"""
    hit = 0
    for line in lines:
        if pattern_hot.search(line) is not None:
            hit += 1
    return hit

print(count_lines_with_date(["日期 2024-01-15", "日期 2024-02-20", "没有日期"]))   # 2
# Java 对照写法：
#   private static final Pattern DATE_PATTERN = Pattern.compile("\\d{4}-\\d{2}-\\d{2}");
#   for (String line : lines) { if (DATE_PATTERN.matcher(line).find()) { hit++; } }

# ⭐⭐⭐ 必会 —— re.IGNORECASE (re.I)：忽略大小写
# Java: Pattern.CASE_INSENSITIVE
print(re.findall(r"python", "Python PYTHON python", re.IGNORECASE))     # ['Python', 'PYTHON', 'python']

# ⭐⭐⭐ 必会 —— re.MULTILINE (re.M)：让 ^ $ 匹配每一行的行首/行尾（默认只匹配整串的开头/结尾）
# Java: Pattern.MULTILINE，行为完全一致
print(re.findall(r"^\w+", "abc\ndef"))              # ['abc']（默认 $ ^ 只看整串）
print(re.findall(r"^\w+", "abc\ndef", re.MULTILINE))    # ['abc', 'def']
# ⚠️ 注意：MULTILINE 不影响 . 是否匹配换行，那是 DOTALL 的事
print(re.findall(r"^$", "a\n\nb", re.MULTILINE))    # ['']（空行占 1 个）

# ⭐⭐⭐ 必会 —— re.DOTALL (re.S)：让 . 也能匹配换行符
# Java: Pattern.DOTALL
print(re.findall(r".+", "第一行\n第二行"))            # ['第一行', '第二行']（. 不跨行）
print(re.findall(r".+", "第一行\n第二行", re.DOTALL)) # ['第一行\n第二行']（贪心吃掉全部）
# 实战：跨行提取 {/* */} 注释
code = "int a; /* 备注\n第二行 */ int b;"
print(re.findall(r"/\*.*?\*/", code, re.DOTALL))    # ['/* 备注\n第二行 */']

# ⭐⭐ 常用 —— re.VERBOSE (re.X)：模式里可以写空白和 # 注释，长正则的救命稻草
# Java: Pattern.COMMENTS，行为一致
# 注意：VERBOSE 下空格会被忽略，真要匹配空格得写 \s 或 [ ]
re_verbose = re.compile(r"""
    (?P<year>\d{4})     # 年
    -                   # 分隔符
    (?P<month>\d{2})    # 月
""", re.VERBOSE)
print(re_verbose.findall("2024-01 2025-12"))        # [('2024', '01'), ('2025', '12')]

# ⭐⭐⭐ 必会 —— flags 用 | 组合（与 Java 的 | 组合完全一样）
# Java: Pattern.CASE_INSENSITIVE | Pattern.MULTILINE
print(re.findall(r"^python$", "Python\npython\nPYTHON", re.IGNORECASE | re.MULTILINE))
# ['Python', 'python', 'PYTHON']（IGNORECASE 管大小写，MULTILINE 让 ^$ 逐行生效）

# 编译时与调用时都能传 flags，二者会「按位或」合并
compiled_i = re.compile(r"python", re.IGNORECASE)
print(compiled_i.findall("Python python"))          # ['Python', 'python']
print(compiled_i.pattern)                           # python


# ==================== 八、元字符与量词速查 ====================

# ⭐⭐ 常用 —— 全部字符必须写在原始字符串 r"..." 里（Java 要写 "\\d"）
#
# 【字符类】
#   .       任意字符（默认不含换行，配 re.DOTALL 才含）   r"a.c"    → abc / a c，不匹配 a\nc
#   \d      数字 [0-9]（含 Unicode 数字）                 r"\d+"    → 123
#   \D      非数字 [^0-9]                                 r"\D+"    → abc
#   \w      单词字符 [a-zA-Z0-9_]（含中文！这点和 Java 不同）
#                                                          r"\w+"    → abc_1
#   \W      非单词字符                                     r"\W+"    → ，。！@#
#   \s      空白（空格 \t \n \r \f \v）                    r"\s+"    → " \t\n"
#   \S      非空白                                         r"\S+"    → abc
#   []      字符集合，内部大部分元字符失去特殊含义          r"[abc]"  → a / b / c
#   [^]     取反                                           r"[^abc]" → 除 abc 外任意字符
#   |       或（注意范围，建议配 (?:) 圈定）                r"cat|dog"→ cat / dog
#
# 【锚点与边界】
#   ^       串首（re.MULTILINE 下为行首）                   r"^abc"   → 以 abc 开头
#   $       串尾（re.MULTILINE 下为行尾）                   r"abc$"   → 以 abc 结尾
#   \b      单词边界                                       r"\bcat\b"→ 独立单词 cat
#   \B      非单词边界                                     r"\Bcat\B"→ scats 里的 cat
#
# 【量词】
#   *       0 次或多次（贪婪）                             r"ab*"    → a / ab / abbb
#   +       1 次或多次（贪婪）                             r"ab+"    → ab / abbb
#   ?       0 次或 1 次（贪婪）                            r"ab?"    → a / ab
#   {n}     恰好 n 次                                      r"\d{4}"  → 2024
#   {n,}    n 次或更多                                     r"\d{4,}" → 2024 / 20240101
#   {n,m}   n 到 m 次                                      r"\d{2,4}"→ 20 / 2024
#   量词后加 ? 变非贪婪                                     r"<.*?>"  → 最短匹配
#
# 【转义】
#   \       转义元字符，或引用反向引用 \1 \g<name>          r"\.", r"\\"
#
# 【分组】
#   (...)          捕获分组                                r"(\d+)-(\d+)"
#   (?:...)        非捕获分组                              r"(?:ab)+"
#   (?P<n>...)     命名捕获分组（Java 是 (?<n>...)）        r"(?P<y>\d{4})"
#   (?P=n)         命名反向引用（Java 是 \k<n>）            r"(?P<c>\w)(?P=c)"
#   (?=...) (?!...) (?<=...) (?<!...)   四种断言，见第九节

# ⭐⭐⭐ 必会 —— 单词边界 \b：\b 是「\w 和 \W 的交界处」，不是字符，不占宽度
print(re.findall(r"\bcat\b", "cat category cat."))      # ['cat', 'cat']
print(re.findall(r"\Bcat\B", "scats"))                  # ['cat']

# ⭐⭐⭐ 必会 —— \w 在 Python 里默认匹配中文！（Java 默认不匹配，这是重大差异）
# Java: \w 默认等价于 [a-zA-Z_0-9]；Python 默认是 Unicode 语义
print(re.findall(r"\w+", "abc_1 中文 123"))             # ['abc_1', '中文', '123']
# 想回到 Java / ASCII 语义 → 加 re.ASCII
print(re.findall(r"\w+", "abc_1 中文 123", re.ASCII))    # ['abc_1', '123']

# ⭐⭐⭐ 必会 —— 贪婪 vs 非贪婪：默认贪婪（尽可能多），量词后加 ? 变非贪婪（尽可能少）
html = "<b>粗体</b><i>斜体</i>"
print(re.findall(r"<.*>", html))        # ['<b>粗体</b><i>斜体</i>']（贪婪：一口气吃到最后一个 >）
print(re.findall(r"<.*?>", html))       # ['<b>', '</b>', '<i>', '</i>']（非贪婪：吃到最近的一个 >）
print(re.findall(r"<[^>]+>", html))     # ['<b>', '</b>', '<i>', '</i>']（用取反字符集也能达到同样效果）

# 非贪婪的经典翻车场景：匹配引号内容（结尾定界符能在内容里出现时，非贪婪会提前收手）
print(re.findall(r'".*?"', '"a" and "b"'))              # ['"a"', '"b"']
print(re.findall(r'"[^"]*"', '"a" and "b"'))            # ['"a"', '"b"']（这个更稳）

# 数量词也能非贪婪
print(re.match(r"\d+", "123456").group())               # 123456
print(re.match(r"\d+?", "123456").group())              # 1

# ⭐⭐⭐ 必会 —— . 默认不匹配换行，跨行必须 re.DOTALL
print(re.findall(r"a.b", "a\nb"))                       # []
print(re.findall(r"a.b", "a\nb", re.DOTALL))            # ['a\nb']
# 💡 反直觉点：字符集 [] 里的 . 就是普通点号，r"[.]" 等于 r"\."
print(re.findall(r"[.]", "a.b.c"))                      # ['.', '.']


# ==================== 九、断言（零宽，不消耗字符）====================

# ⭐ 了解 —— 前瞻 (?=...)：后面必须是什么，但断言内容不进入 match.group()
# Java: 语法完全一致（Java 不支持变长后顾，Python 同样不支持）
# 场景：取价格的数字，但不要"元"字
print(re.findall(r"\d+(?=元)", "苹果5元，香蕉12元，美元20"))     # ['5', '12']

# ⭐ 了解 —— 否定前瞻 (?!...)：后面不能是什么
print(re.findall(r"\d+(?!元)", "苹果5元，香蕉12元，美元20"))     # ['1', '20']
# 💡 为什么是 ['1','20'] 而不是 ['20']？这就是否定前瞻的经典陷阱：
#    "5元" 处 \d+ 先贪婪吃掉 "5"，前瞻发现后面是"元"→失败，回溯到 1 位以下不允许→整体放弃；
#    "12元" 处先吃 "12"，前瞻发现后面是"元"→失败，回溯成 "1"，此时后面是 "2" 不是"元"→成功！
#    于是只捞到了半个数字 "1"。
#    ⚠️ 结论：凡是"排除某后缀"的需求，优先用字符集 r"\d+(?![元\d])" 或先 findall 再过滤，
#       别指望 (?!...) 能自动帮你保证匹配边界完整。

# ⭐ 了解 —— 后顾 (?<=...)：前面必须是什么（断言部分长度必须固定）
# Java: (?<=...) 一致
print(re.findall(r"(?<=￥)\d+", "￥100 ￥200 $300"))             # ['100', '200']

# ⭐ 了解 —— 否定后顾 (?<!...)
print(re.findall(r"(?<!￥)\b\d+\b", "￥100 200 $300"))           # ['200', '300']

# 断言实战：密码强度校验（至少 8 位，且必须同时含字母和数字）
# Java: 同样靠一串 (?=.*\\d) 的"预检"写法
def check_password(pwd: str) -> bool:
    """密码必须 8 位以上，且同时包含字母和数字"""
    return re.fullmatch(r"(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}", pwd) is not None

print(check_password("abcd1234"))       # True
print(check_password("abcdefgh"))       # False
print(check_password("abc123"))         # False（不足 8 位）

# 断言实战：千分位分隔（从右往左每三位插一个逗号）
def add_thousands_sep(num_str: str) -> str:
    """1234567 → 1,234,567"""
    return re.sub(r"(?<=\d)(?=(\d{3})+$)", ",", num_str)

print(add_thousands_sep("1234567"))     # 1,234,567
print(add_thousands_sep("1000"))        # 1,000


# ==================== 十、re.escape ====================

# ⭐ 了解 —— 把字符串里的正则元字符全部转义，让它变成"纯字面量"
# Java: Pattern.quote(...)  —— 一一对应
# 什么时候必须用：把「用户输入」「数据库里的关键字」拼进正则时。
# 不转义的话，用户输入一个 "." 或 "*" 就能构造出意料之外的匹配（正则注入）
raw = "1+1=2? (a)[b]"
print(re.escape(raw))                           # 1\+1=2\?\ \(a\)\[b\]
print(re.escape("C:\\Users"))                   # C:\\Users

# 危险写法（用户搜 "." 会匹配到所有字符）
print(len(re.findall(".", "abc")))              # 3
# 安全写法
user_input = "."
print(len(re.findall(re.escape(user_input), "abc")))    # 0（只找真正的点号）

# 实用封装：按关键字模糊搜索（字面量包含）
def contains_keyword(text: str, keyword: str) -> bool:
    """判断 text 中是否包含 keyword（纯字面量，keyword 里的正则符号不生效）"""
    return re.search(re.escape(keyword), text) is not None

print(contains_keyword("a.b.c", "."))           # True
print(contains_keyword("abc", "."))             # False


# ==================== 十一、实战案例 ====================

# ⭐⭐⭐ 必会 —— 案例1：中国大陆手机号校验
# Java: Pattern.compile("^1[3-9]\\d{9}$").matcher(phone).matches()
# ⚠️ Python 校验必须用 fullmatch，或者自己补 ^...$；用 match 会漏判 "13812345678abc"
PHONE_RE = re.compile(r"1[3-9]\d{9}")

def is_valid_phone(phone: str) -> bool:
    """校验中国大陆手机号"""
    return PHONE_RE.fullmatch(phone) is not None

print(is_valid_phone("13812345678"))    # True
print(is_valid_phone("12812345678"))    # False（第 2 位必须是 3-9）
print(is_valid_phone("1381234567"))     # False（位数不够）
print(is_valid_phone("138123456789"))   # False（位数超了）
print(is_valid_phone("1381234567a"))    # False

# ⭐⭐⭐ 必会 —— 案例2：从一段文本里提取所有邮箱
# 注意 TLD 用 [A-Za-z]{2,} 限制，否则 "a@b.c" 这种脏数据也会被捞出来
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

def extract_emails(text: str) -> list:
    """提取文本中所有邮箱地址"""
    return EMAIL_RE.findall(text)

sample = "联系人：张三 zhangsan@example.com，李四 li.si@corp.com.cn，无效的 a@b"
print(extract_emails(sample))   # ['zhangsan@example.com', 'li.si@corp.com.cn']

# 同时提取用户名和域名（用分组）
EMAIL_PARTS_RE = re.compile(r"([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")

def extract_email_parts(text: str) -> list:
    """提取 (用户名, 域名) 元组列表"""
    return EMAIL_PARTS_RE.findall(text)

print(extract_email_parts(sample))      # [('zhangsan', 'example.com'), ('li.si', 'corp.com.cn')]

# ⭐⭐⭐ 必会 —— 案例3：日志解析（命名分组的典型应用场景）
# Java: Pattern.compile("(?<time>...)\\s+(?<level>...)...")
# Java: 之前只能靠 split + 下标取值，命名分组可读性高一个数量级
LOG_RE = re.compile(
    r"(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"    # 时间
    r"\s+"
    r"(?P<level>[A-Z]+)"                                 # 级别
    r"\s+"
    r"\[(?P<thread>[^\]]+)\]"                            # 线程名（用 [^\]]+ 而非 .+ 防止吃掉后面的内容）
    r"\s+"
    r"(?P<message>.+)"                                   # 消息
)

def parse_log_line(line: str):
    """解析单行日志，返回字典；解析失败返回 None"""
    mt = LOG_RE.match(line)
    if mt is None:
        return None
    return mt.groupdict()

LOG_SAMPLE = "2024-01-15 10:23:45 ERROR [main] 连接超时"

print(parse_log_line(LOG_SAMPLE))
# {'time': '2024-01-15 10:23:45', 'level': 'ERROR', 'thread': 'main', 'message': '连接超时'}

parsed = parse_log_line(LOG_SAMPLE)
print(parsed["level"], parsed["thread"], parsed["message"])     # ERROR main 连接超时

def parse_log_lines(text: str) -> list:
    """解析多行日志，跳过解析不了的行"""
    result = []
    for line in text.splitlines():
        item = parse_log_line(line)
        if item is not None:
            result.append(item)
    return result

LOG_BLOCK = """2024-01-15 10:23:45 ERROR [main] 连接超时
这是一行不是日志的干扰内容
2024-01-15 10:23:46 INFO [http-nio-8080-exec-1] 请求处理完成"""
records = parse_log_lines(LOG_BLOCK)
print(f"[{records[0]['level']}] {records[0]['thread']} -> {records[0]['message']}")   # [ERROR] main -> 连接超时
print(f"[{records[1]['level']}] {records[1]['thread']} -> {records[1]['message']}")   # [INFO] http-nio-8080-exec-1 -> 请求处理完成
# 💡 干扰行被 parse_log_line 返回的 None 过滤掉了，len(records) 是 2 而不是 3

# 统计各级别日志条数（Java 里通常这么干：Map<级别, 计数>）
def count_by_level(text: str) -> dict:
    """统计各日志级别出现次数"""
    counts = {}
    for record in parse_log_lines(text):
        lv = record["level"]
        counts[lv] = counts.get(lv, 0) + 1
    return counts

print(count_by_level(LOG_BLOCK))        # {'ERROR': 1, 'INFO': 1}

# ⭐⭐⭐ 必会 —— 案例4：驼峰转下划线 / 下划线转驼峰
# Java: 通常引 Guava 的 CaseFormat.UPPER_CAMEL.to(CaseFormat.LOWER_UNDERSCORE, s)
# Java: HumpUtil / 手写 StringBuilder 遍历（要处理连续大写，很啰嗦）
def camel_to_snake(name: str) -> str:
    """驼峰转下划线：userName → user_name，HTTPServer → http_server"""
    # 第一刀：在小写字母/数字后紧跟大写字母处断开
    step1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    # 第二刀：处理连续大写结尾接小写的情况
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", step1).lower()

print(camel_to_snake("userName"))           # user_name
print(camel_to_snake("userLoginCount"))     # user_login_count
print(camel_to_snake("HTTPServer"))         # http_server
print(camel_to_snake("already_snake"))      # already_snake

def snake_to_camel(name: str) -> str:
    """下划线转小驼峰：user_name → userName"""
    # 用函数替换，比 str.split + capitalize 更紧凑；_+ 同时吃掉连续下划线
    return re.sub(r"_+([a-zA-Z0-9])", lambda mt: mt.group(1).upper(), name)

print(snake_to_camel("user_name"))          # userName
print(snake_to_camel("user_login_count"))   # userLoginCount
print(snake_to_camel("user__name"))         # userName

def snake_to_pascal(name: str) -> str:
    """下划线转大驼峰（类名）：user_name → UserName"""
    return re.sub(r"(?:^|_+)([a-zA-Z0-9])", lambda mt: mt.group(1).upper(), name)

print(snake_to_pascal("user_name"))         # UserName
print(snake_to_pascal("order_detail_id"))   # OrderDetailId

# ⭐⭐⭐ 必会 —— 案例5：去除 HTML 标签 / 提取纯文本
# Java: 大多用 Jsoup 的 Jsoup.parse(html).text()
# 注意：正则解析 HTML 不是万能的（HTML 不是正则语言），简单清洗够用，复杂场景还是上解析器
TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE)

def strip_html(html: str) -> str:
    """去掉所有标签，返回纯文本"""
    return TAG_RE.sub("", html)

def html_to_text(html: str) -> str:
    """去掉 script/style 块 + 去标签 + 压缩空白"""
    cleaned = SCRIPT_RE.sub("", html)
    cleaned = TAG_RE.sub("", cleaned)
    # HTML 实体简单替换
    cleaned = cleaned.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return re.sub(r"\s+", " ", cleaned).strip()

HTML_SAMPLE = "<p>Hello <b>World</b></p>"
print(strip_html(HTML_SAMPLE))          # Hello World

HTML_PAGE = """<html><head><style>body{color:red}</style></head>
<body><h1>标题</h1><p>正文&nbsp;内容</p><script>var a=1;</script></body></html>"""
print(html_to_text(HTML_PAGE))          # 标题正文 内容

# 提取所有链接的 href（分组 + findall 组合）
LINK_RE = re.compile(r'<a\s+[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)

def extract_links(html: str) -> list:
    """提取 (链接, 锚文本) 列表，锚文本会去掉内部标签"""
    return [(href, strip_html(text).strip()) for href, text in LINK_RE.findall(html)]

print(extract_links('<a href="/a">首页</a> <a class="x" href="/b"><b>关于</b>我们</a>'))
# [('/a', '首页'), ('/b', '关于我们')]

# ⭐⭐⭐ 必会 —— 案例6：敏感信息脱敏
# Java: 通常写工具类 MaskUtil，用 substring 拼接
def mask_phone(phone: str) -> str:
    """手机号中间四位打码：13812345678 → 138****5678"""
    return re.sub(r"(\d{3})\d{4}(\d{4})", r"\1****\2", phone)

def mask_id_card(id_card: str) -> str:
    """身份证保留前 6 后 4：110101199001011234 → 110101********1234"""
    return re.sub(r"^(.{6}).+(.{4})$", r"\1********\2", id_card)

def mask_email(email: str) -> str:
    """邮箱用户名保留前 2 位：zhangsan@example.com → zh******@example.com"""
    return re.sub(r"^([^@]{1,2})[^@]*(@.+)$", r"\1******\2", email)

def mask_bank_card(card: str) -> str:
    """银行卡只保留后 4 位，并按 4 位一组重新排版：6222 0212 3456 7890 → **** **** **** 7890"""
    digits = re.sub(r"\D", "", card)                        # 先剔除空格等非数字
    masked = re.sub(r"\d(?=\d{4})", "*", digits)            # 后面还跟着至少 4 位数字 → 打码，最终只剩后 4 位
    return " ".join(masked[i:i + 4] for i in range(0, len(masked), 4))

print(mask_phone("13812345678"))                        # 138****5678
print(mask_id_card("110101199001011234"))               # 110101********1234
print(mask_email("zhangsan@example.com"))               # zh******@example.com
print(mask_bank_card("6222 0212 3456 7890"))            # **** **** **** 7890

# 一站式脱敏：一段文本里所有手机号全部打码（sub + 函数替换）
def mask_all_phones(text: str) -> str:
    """把文本里所有手机号批量打码"""
    return re.sub(r"\b(1[3-9]\d)\d{4}(\d{4})\b", r"\1****\2", text)

print(mask_all_phones("张三 13812345678，李四 15987654321"))   # 张三 138****5678，李四 159****4321


# ==================== 十二、Java 开发者踩坑清单 ====================
#
# 1. re.match ≠ Java 的 matches()        → 校验格式一律用 re.fullmatch
# 2. 字符串忘了加 r 前缀                  → r"\d+" 而不是 "\d+"（Java 要写 "\\d+"）
# 3. 结果忘了判 None                      → 直接 .group() 会抛 AttributeError
# 4. 命名分组写成 Java 的 (?<name>...)    → Python 是 (?P<name>...)
# 5. 替换串反向引用写成 $1                → Python 是 \1 或 \g<name>
# 6. findall 加了分组结果变元组           → 不想要就写非捕获分组 (?:...)
# 7. \w 在 Python 默认匹配中文            → 要 Java 语义加 re.ASCII
# 8. 循环里反复 re.match 而不预编译       → 热点路径先 re.compile
# 9. . 不匹配换行                         → 跨行加 re.DOTALL
# 10. 用户输入直接拼进正则                → 必须 re.escape（等价 Java 的 Pattern.quote）
#
# 统一记忆口诀：
#   校验用 fullmatch，取值用 search，全取用 findall，换位用 sub 的反向引用。

print("=== 19 正则表达式 结束 ===")
