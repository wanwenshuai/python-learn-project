"""
===== 第22课：并发与异步 =====
对标 Java 的 Thread / ExecutorService / CompletableFuture / 虚拟线程

第 11 课已讲过 Thread / ThreadPoolExecutor / Pool 的基础用法，本课往深讲：
GIL 的本质、竞态与锁、线程安全队列、Future 高级用法、asyncio 事件循环、阻塞陷阱、选型。

⚠️⚠️⚠️ 本文件最重要的约束：multiprocessing / ProcessPoolExecutor 必须放在
        if __name__ == "__main__": 保护块内（本文件把所有执行逻辑都放进了 main()）。
   原因：macOS / Windows 用 spawn 方式启动子进程，子进程会「重新 import 本模块」。
        - 若在模块顶层创建进程池 → 子进程 import 时又创建进程池 → 无限自我复制（进程爆炸，实测卡死）
        - 若在模块顶层写 print → 子进程 import 时会把顶层 print 重复打印一遍
   所以：模块顶层只允许有 import、常量、函数/类定义，一行执行语句都不要有。
   Linux 默认 fork 模式可以侥幸不写，但绝对不要依赖这个差异。
"""

import asyncio
import queue
import sys
import threading
import time
from concurrent.futures import (
    FIRST_COMPLETED,
    ProcessPoolExecutor,
    ThreadPoolExecutor,
    as_completed,
    wait,
)

# ==================== 模块顶层：只放函数定义与常量（spawn 安全） ====================

# CPU 密集型任务：纯计算，不涉及 IO，不会主动释放 GIL
def burn_cpu(n: int) -> int:
    """把 0..n-1 的平方累加，纯 CPU 计算（务必不要写太大，否则跑很久）"""
    total = 0
    for i in range(n):
        total += i * i
    return total


# 模拟一次网络/磁盘 IO：用 sleep 代替真实请求，保证脚本离线可运行
def fetch_data(task_id: int, delay: float) -> str:
    time.sleep(delay)
    return f"任务{task_id}完成(耗时{delay}s)"


def step() -> int:
    """计数器每次的增量。

    注意：函数调用点是 CPython 的「线程切换检查点」。
    正是它让下面「读-改-写」三步之间出现可被抢占的窗口，竞态才能稳定复现。
    """
    return 1


def add_unsafe(loops: int, state: dict) -> None:
    """无锁累加：state['count'] = state['count'] + step() 不是原子操作"""
    for _ in range(loops):
        state["count"] = state["count"] + step()


def add_safe(loops: int, state: dict, lock: threading.Lock) -> None:
    """加锁累加：with lock 保证临界区同一时刻只有一个线程能进"""
    for _ in range(loops):
        with lock:
            state["count"] = state["count"] + step()


def add_reentrant(loops: int, state: dict, lock: threading.RLock) -> None:
    """可重入锁演示：同一个线程可以多次 acquire 同一把 RLock"""
    for _ in range(loops):
        with lock:                      # 第一次加锁
            with lock:                  # 同一线程再进一次，RLock 允许；换成 Lock 会死锁
                state["count"] = state["count"] + step()


def producer(q: queue.Queue, name: str, items: list) -> None:
    """生产者：往线程安全队列里放数据"""
    for item in items:
        time.sleep(0.01)                # 模拟生产耗时
        q.put(item)
        print(f"  [{name}] 生产 {item}")


def consumer(q: queue.Queue, name: str) -> None:
    """消费者：从队列取数据，收到 None 哨兵就退出"""
    while True:
        item = q.get()
        try:
            if item is None:
                print(f"  [{name}] 收到结束信号，退出")
                return
            time.sleep(0.01)            # 模拟消费耗时
            print(f"  [{name}] 消费 {item}")
        finally:
            q.task_done()               # 必须调用，q.join() 才能返回


async def say_after(delay: float, msg: str) -> str:
    """协程函数：async def 定义，await 处挂起并让出控制权"""
    await asyncio.sleep(delay)          # 异步 sleep，等价于 Java 的延迟任务，但不占线程
    return msg


async def serial_three() -> float:
    """串行 await 三次 sleep(1)：总耗时 ≈ 3 秒"""
    start = time.perf_counter()
    await asyncio.sleep(1)              # 一次只发一个请求，等它回来再发下一个
    await asyncio.sleep(1)
    await asyncio.sleep(1)
    return time.perf_counter() - start


async def concurrent_three() -> float:
    """asyncio.gather 并发三次 sleep(1)：总耗时 ≈ 1 秒"""
    start = time.perf_counter()
    await asyncio.gather(
        asyncio.sleep(1),
        asyncio.sleep(1),
        asyncio.sleep(1),
    )
    return time.perf_counter() - start


async def maybe_fail(task_id: int, fail: bool) -> str:
    """可能抛异常的协程，用来演示 gather(return_exceptions=True)"""
    await asyncio.sleep(0.05)
    if fail:
        raise ValueError(f"任务{task_id}业务失败")
    return f"任务{task_id}成功"


async def async_producer(q: "asyncio.Queue", items: list) -> None:
    for item in items:
        await asyncio.sleep(0.01)
        await q.put(item)
    await q.put(None)                   # 哨兵


async def async_consumer(q: "asyncio.Queue", name: str) -> int:
    count = 0
    while True:
        item = await q.get()
        if item is None:
            await q.put(None)           # 唤醒下一个消费者
            return count
        await asyncio.sleep(0.01)
        count += 1
        print(f"  [{name}] 消费 {item}")
    return count


async def slow_forever() -> str:
    await asyncio.sleep(10)             # 故意超长，配合 wait_for 超时
    return "永远等不到"


async def blocking_task() -> str:
    """错误的异步代码：在协程里调用阻塞的 time.sleep"""
    time.sleep(1)                       # ⚠️ 阻塞整个事件循环，其它协程全部停摆
    return "阻塞任务完成"


async def non_blocking_task() -> str:
    """正确的异步代码：用 asyncio.sleep"""
    time.sleep(0)                       # 占位，无实际作用
    await asyncio.sleep(1)
    return "非阻塞任务完成"


async def quick_task(start: float) -> str:
    """只等 0.1 秒的快速任务，用来证明它被前一个阻塞任务拖累了。

    start 是整个演示的起始时刻，返回「它完成时距离演示开始过了多久」。
    ⚠️ 注意：不能在这个协程内部自己掐表 —— 被阻塞时它根本轮不到执行，
       自己掐的表永远显示 0.10s，完全看不出异常。
    """
    await asyncio.sleep(0.1)
    return f"快速任务在演示开始后 {time.perf_counter() - start:.2f}s 才完成"


async def fake_request(idx: int) -> str:
    """模拟一次网络请求：0.1~0.5 秒随机延迟"""
    import random
    await asyncio.sleep(random.uniform(0.1, 0.5))
    return f"请求{idx}返回"


# ==================== 一、GIL 是什么 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
# Java: 完全没有这个概念，JVM 里 4 个线程就是实实在在地跑在 4 个核上
# Python: GIL = Global Interpreter Lock（全局解释器锁），CPython 解释器同一时刻
#         只允许「一个线程」执行 Python 字节码
#
# 后果 1：多线程无法加速 CPU 密集型任务（这是 Python 与 Java 最大的差异）
# 后果 2：多线程对 IO 密集型任务依然有效 —— 线程在等待 IO 时会主动释放 GIL
def demo_01_gil() -> None:
    print("\n=== 一、GIL 是什么 ===")
    work = 2_000_000

    # 先看单线程串行跑 4 次 CPU 任务
    start = time.perf_counter()
    for _ in range(4):
        burn_cpu(work)
    serial_cost = time.perf_counter() - start
    print(f"单线程串行跑 4 次 CPU 任务: {serial_cost:.2f}s   # 输出示例（约 0.35s，机器不同会有差异）")

    # 再用 4 个线程跑同样的 4 次任务
    threads = [threading.Thread(target=burn_cpu, args=(work,)) for _ in range(4)]
    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    thread_cost = time.perf_counter() - start
    print(f"4 线程并行跑 4 次 CPU 任务: {thread_cost:.2f}s   # 输出示例（约 0.35s，几乎不比单线程快）")

    # Java 里同样的代码用 4 线程能提速约 4 倍，Python 不能 —— 这就是 GIL
    print(f"加速比: {serial_cost / thread_cost:.2f}x   # 输出示例（约 1.0x，即完全没加速）")

    # ---------- 结论表格（背下来） ----------
    # 任务类型    | 推荐方案                       | 原因
    # -----------|-------------------------------|--------------------------------
    # CPU 密集    | multiprocessing / 进程池       | 每个进程一个独立解释器，各有各的 GIL
    # IO 密集(少) | threading / ThreadPoolExecutor | 等 IO 时释放 GIL，线程能重叠等待
    # IO 密集(多) | asyncio                        | 单线程事件循环，百万级并发，无切换成本
    #
    # ---------- 对比 Java 21 的虚拟线程 ----------
    # Java 虚拟线程解决的是「IO 密集场景下平台线程太重（1MB 栈 + 内核调度）」的问题，
    # 让「一个请求一个线程」的同步写法也能扛住百万并发。
    # Python 的问题恰好相反：不是线程太重，而是 GIL 让线程根本没法并行跑字节码。
    # 所以 Java 21 虚拟线程 ≈ Python 的 asyncio（都是 IO 密集场景的解法），
    # 但 Java 的虚拟线程不需要你把代码改成 await 风格，也不用担心「阻塞陷阱」（见第八节）。
    #
    # ---------- Python 3.13 的 free-threaded（PEP 703） ----------
    # 3.13 开始提供「可关闭 GIL」的实验性构建（python3.13t），用 --disable-gil 编译。
    # 关掉 GIL 后多线程可以真正并行，但：生态兼容性差、单线程性能有损耗、仍是实验特性。
    # 生产环境目前仍然按「GIL 存在」来做技术选型。


# ==================== 二、threading 基础 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
def demo_02_threading() -> None:
    print("\n=== 二、threading 基础 ===")

    # Java: new Thread(() -> {...}).start();
    # Python: Thread(target=函数, args=(参数元组,)) —— 注意 args 必须是元组，单参数要写 (x,)
    def worker(name: str, delay: float) -> None:
        print(f"  [{name}] 开始")
        time.sleep(delay)               # 模拟 IO 等待，此时会释放 GIL
        print(f"  [{name}] 结束")

    # ---- 场景 1：不 join，主线程不等子线程 ----
    # Java: 不调用 join() 效果一样（主线程直接往下跑）
    threads = [
        threading.Thread(target=worker, args=(f"不join-T{i}", 0.05 * (3 - i)))
        for i in range(3)
    ]
    for t in threads:
        t.start()
    print("  主线程没等子线程，直接打印这一行")     # 输出：这行可能夹在任意两行子线程输出之间
    for t in threads:
        t.join()                        # 收尾，保证后面的演示不被干扰
    # 输出示例（顺序不定）：可能的顺序是
    #   [不join-T0] 开始 / [不join-T1] 开始 / 主线程没等子线程... / [不join-T2] 开始 / ...
    # 结论：不 join 时主线程先结束，输出顺序完全不可控

    # ---- 场景 2：join 等待 ----
    # Java: t.join() —— 一模一样
    threads = [
        threading.Thread(target=worker, args=(f"join-T{i}", 0.05))
        for i in range(3)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()                        # 阻塞直到该线程结束
    print("  三个子线程全部结束后才打印这一行")     # 输出：一定在三个 [join-Tx] 结束 之后

    # ---- 场景 3：daemon 守护线程 ----
    # Java: thread.setDaemon(true) —— 必须在 start() 之前调用
    # Python: Thread(daemon=True)，同样必须在 start() 之前设置
    d = threading.Thread(target=worker, args=("daemon-T", 0.05), daemon=True)
    print(f"  daemon 属性: {d.daemon}")            # True
    d.start()
    d.join()
    # Python 也支持 start() 之前调用 d.setDaemon(True)（老写法，等价于 daemon=True）

    # 主线程是「非 daemon 线程」；只要还有非 daemon 线程活着，进程就不退出。
    # daemon 线程在「所有非 daemon 线程结束」时被直接杀死（不执行 finally）。
    # 真实验证放在 main() 的最后一行，见「daemon 线程被杀」演示。
    print("  daemon 线程的杀死效果在 main() 结尾演示")


# ==================== 三、竞态条件与锁 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
def demo_03_race_and_lock() -> None:
    print("\n=== 三、竞态条件与锁 ===")
    loops = 100_000
    n_threads = 4
    expect = loops * n_threads

    # 把线程切换阈值调小，让「检查点」处更容易发生切换，竞态稳定复现
    # （默认是 0.005 秒；这只影响演示效果，不影响结论）
    old_interval = sys.getswitchinterval()
    sys.setswitchinterval(1e-5)

    # ---- 步骤 1：先看 bug ----
    # Java: 多个线程 counter++ 同样有这个问题，i++ 也是「读-改-写」三步
    state = {"count": 0}
    threads = [
        threading.Thread(target=add_unsafe, args=(loops, state))
        for _ in range(n_threads)
    ]
    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    cost = time.perf_counter() - start
    print(f"无锁结果: {state['count']} / 期望 {expect}   # 输出示例（约 160000 / 400000，稳定小于期望）")
    print(f"无锁耗时: {cost:.3f}s   # 输出示例（约 0.04s）")

    # 为什么少了？
    #   state["count"] = state["count"] + step()
    #   第 1 步 读：把 count 读进寄存器      ← 这里可能被切换
    #   第 2 步 改：加 1
    #   第 3 步 写：写回 count               ← 另一个线程也写了同样的旧值，本次自增被覆盖
    #
    # ⚠️ 进阶真相（本课重点）：CPython 3.10+ 的 GIL 只在「检查点」才可能切换线程，
    #    检查点是函数调用、循环回跳等少数几条指令。
    #    如果你写的是紧挨着的三行 `counter += 1`，中间没有检查点，在 3.13 上极难复现（实测 100% 正确）。
    #    所以「加锁」这件事不能靠运气：临界区一旦跨函数调用（真实业务几乎必然如此），
    #    ORM 查询、日志、RPC 都在中间，丢更新就会稳定发生 —— 上面的 step() 调用就是模拟这个窗口。
    #    在 free-threaded（PEP 703）构建下没有 GIL，`counter += 1` 会真真切切地丢更新。

    # ---- 步骤 2：加锁后再跑一遍 ----
    # Java: synchronized (lock) { counter++; }  /  ReentrantLock.lock() ... finally unlock()
    lock = threading.Lock()
    state = {"count": 0}
    threads = [
        threading.Thread(target=add_safe, args=(loops, state, lock))
        for _ in range(n_threads)
    ]
    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    cost = time.perf_counter() - start
    print(f"加锁结果: {state['count']} / 期望 {expect}   # 400000（每次都精确等于期望）")
    print(f"加锁耗时: {cost:.3f}s   # 输出示例（约 0.08s，比无锁慢约一倍，这是并发的必要代价）")

    # ---- 步骤 3：RLock 可重入锁 ----
    # Java: ReentrantLock 就是可重入的；Python 的 Lock 不可重入，RLock 才是
    rlock = threading.RLock()
    state = {"count": 0}
    threads = [
        threading.Thread(target=add_reentrant, args=(loops, state, rlock))
        for _ in range(n_threads)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"RLock 可重入结果: {state['count']} / 期望 {expect}   # 400000")

    sys.setswitchinterval(old_interval)     # 恢复默认，避免影响后面的演示性能

    # ---- 为什么 GIL 不能替代锁？ ----
    # GIL 只保证「单条字节码」是原子的。它管不了你的业务逻辑：
    #   if user.balance >= amount:      ← 检查（原子）
    #       user.balance -= amount      ← 扣减（原子）
    #   两步各自原子，合起来不原子 —— 中间照样会被切走，超卖就是这么来的。
    # 对比 Java：JVM 也没有「业务原子性」的保证，同样需要 synchronized / CAS。
    # 一句话：GIL 是解释器的实现细节，锁是你业务正确性的保证，两者不能互相替代。
    #
    # 正确姿势：
    #   1) 优先「无共享状态」—— 每个线程算自己的，最后汇总（map-reduce 思路）
    #   2) 必须共享时用 queue.Queue（第四节，天生线程安全）
    #   3) 再不行才用 Lock，临界区越小越好


# ==================== 四、线程安全的数据结构 ====================
# ⭐⭐ 常用 —— 经常用
def demo_04_queue() -> None:
    print("\n=== 四、线程安全的数据结构 queue.Queue ===")

    # Java: BlockingQueue<String> q = new ArrayBlockingQueue<>(100);
    #       q.put(x) / q.take() —— Python 的 queue.Queue 语义几乎是 1:1 对应
    # queue.Queue 内部自带锁，put/get 天生线程安全，不用你再加锁
    q: queue.Queue = queue.Queue(maxsize=10)   # 有界队列，满了 put 会阻塞（≈ ArrayBlockingQueue）
    # queue.Queue()    → 无界，≈ LinkedBlockingQueue
    # queue.LifoQueue()→ 后进先出，≈ LinkedBlockingDeque 的栈用法
    # queue.PriorityQueue() → 优先队列，≈ PriorityBlockingQueue

    producers = [
        threading.Thread(target=producer, args=(q, f"生产者{i}", [f"数据{i}-{j}" for j in range(4)]))
        for i in range(2)
    ]
    consumers = [threading.Thread(target=consumer, args=(q, f"消费者{i}")) for i in range(2)]

    for t in consumers:
        t.start()
    for t in producers:
        t.start()
    for t in producers:
        t.join()
    # 2 个生产者各生产 4 条，生产完毕再放 2 个哨兵通知消费者退出
    q.put(None)
    q.put(None)
    for t in consumers:
        t.join()
    q.join()                        # 等所有 task_done() 调用完（Java: 无直接等价物）
    print(f"队列剩余: {q.qsize()}   # 0")
    # 输出示例（顺序不定）：两个生产者和两个消费者交错打印，
    #   可能的顺序是 [生产者0] 生产 数据0-0 / [消费者1] 消费 数据0-0 / [生产者1] 生产 数据1-0 ...
    #   但绝不会出现「同一条数据被消费两次」—— 这是 Queue 内部锁保证的

    # ---- 为什么用 Queue 而不是 list？ ----
    # list.append / list.pop 是单条字节码、看起来「原子」，但它们不是为并发设计的：
    #   if len(lst) > 0:        ← 检查
    #       item = lst.pop()    ← 取值（中间被切走就 IndexError / 重复消费）
    # Java 同理：ArrayList 不是线程安全的，要用 BlockingQueue 或 ConcurrentLinkedQueue。
    # Python 里线程安全的现成结构：
    #   queue.Queue           → 队列（最常用）
    #   collections.deque     → append/popleft 本身原子，适合做轻量双端队列
    #   dict / list 的「单次读或单次写」→ 靠 GIL 是安全的，但「读-改-写」不安全


# ==================== 五、concurrent.futures 线程池与进程池 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
def demo_05_executors() -> None:
    print("\n=== 五、concurrent.futures 线程池与进程池 ===")

    # Java: ExecutorService pool = Executors.newFixedThreadPool(4);
    #       Future<String> f = pool.submit(() -> ...); f.get();
    # Python: ThreadPoolExecutor(max_workers=4)  ≈ 固定大小线程池
    #         必须用 with 管理（≈ try-with-resources），退出时自动 shutdown() 并等待任务完成

    # ---- 5.1 Future 对象常用方法 ----
    with ThreadPoolExecutor(max_workers=1) as pool:
        # result(timeout=) ≈ Java 的 future.get(2, TimeUnit.SECONDS)
        blocker = pool.submit(fetch_data, 0, 0.3)     # 先占住唯一的线程
        pending = pool.submit(fetch_data, 99, 0.1)    # 还在排队，没开始跑
        print(f"cancel 未开始的任务: {pending.cancel()}   # True")
        print(f"cancel 已完成的任务: {blocker.cancel()}   # False（已在执行，取消不掉）")
        print(f"done 是否完成: {blocker.done()}   # 输出示例（False 或 True，取决于此刻是否跑完）")
        print(f"result 阻塞取结果: {blocker.result()}   # 任务0完成(耗时0.3s)")
        print(f"done 完成之后再查: {blocker.done()}   # True")
        print(f"exception 无异常时: {blocker.exception()}   # None")

    # ⚠️ result() 不设 timeout 会一直阻塞（≈ get() 无参）；生产代码一定要给 timeout

    # ---- 5.2 as_completed：谁先完成先拿结果 ----
    # Java: CompletionService<String> cs = new ExecutorCompletionService<>(pool);
    #       for (Future<String> f : ...) cs.take().get();
    delayed = [0.3, 0.1, 0.2, 0.05]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(fetch_data, i, d) for i, d in enumerate(delayed)]
        print("按完成顺序拿结果:")
        for fut in as_completed(futures):
            print(f"  {fut.result()}")
    # 输出（顺序不定，由耗时决定）：
    #   任务3完成(耗时0.05s)
    #   任务1完成(耗时0.1s)
    #   任务2完成(耗时0.2s)
    #   任务0完成(耗时0.3s)

    # ---- 5.3 wait(FIRST_COMPLETED)：等第一个完成就返回 ----
    # Java: 没有直接等价物，一般用 CountDownLatch 或 CompletionService 模拟
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(fetch_data, i, d) for i, d in enumerate([0.1, 0.2, 0.3])]
        done, not_done = wait(futures, return_when=FIRST_COMPLETED)
        print(f"已完成 {len(done)} 个，未完成 {len(not_done)} 个   # 输出示例（已完成 1 个，未完成 2 个）")
        for fut in done:
            print(f"  第一个完成的: {fut.result()}")     # 输出示例：任务0完成(耗时0.1s)
    # 适用场景：多个数据源同时查，谁先返回用谁（对冲请求）

    # ---- 5.4 map：批量提交，按入参顺序返回 ----
    with ThreadPoolExecutor(max_workers=4) as pool:
        # Java: pool.invokeAll(tasks) —— 会阻塞到全部完成
        results = list(pool.map(fetch_data, range(4), [0.1, 0.1, 0.1, 0.1]))
        print(f"map 结果按提交顺序返回: {results[0]}")
        # 任务0完成(耗时0.1s)   —— 注意 map 返回顺序与入参顺序一致，不是完成顺序

    # ---- 5.5 线程池 vs 进程池：CPU 密集型任务 ----
    work = 2_000_000
    jobs = [work] * 4

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(burn_cpu, jobs))
    thread_cost = time.perf_counter() - start
    print(f"线程池跑 4 个 CPU 任务: {thread_cost:.2f}s   # 输出示例（约 0.35s，GIL 导致无加速）")

    # ProcessPoolExecutor ≈ Java 的 ForkJoinPool / 多进程方案（Java 没有内置的进程池）
    # ⚠️ 必须放在 if __name__ == "__main__": 保护块内（本文件放在 main() 里），否则 macOS 上进程爆炸
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4) as pool:
        list(pool.map(burn_cpu, jobs))
    process_cost = time.perf_counter() - start
    print(f"进程池跑 4 个 CPU 任务: {process_cost:.2f}s   # 输出示例（约 0.2s，真并行，比线程池快约一半）")
    # 为什么不是精确的 4 倍？因为 macOS 用 spawn 启动 4 个子进程要各自重新 import 本模块，
    # 这笔固定开销（几十毫秒级）要摊到总耗时里。任务越重，启动开销占比越小，加速比越接近核数；
    # 任务越轻，进程池甚至会比直接用单线程还慢 —— 轻量 CPU 任务不要用进程池。


# ==================== 六、asyncio 入门 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
def demo_06_asyncio_basic() -> None:
    print("\n=== 六、asyncio 入门 ===")

    # Java: CompletableFuture.supplyAsync(() -> ...) + 线程池
    # Python: async def 定义协程 + asyncio.run() 启动事件循环
    # 关键差异：asyncio 是「单线程事件循环」，靠「协作式调度」——
    #   只有代码主动 await 时才切换任务（Java 线程是抢占式调度，随时可能被切走）；
    #   一个协程不 await，整个事件循环就卡住（见第八节）。

    # ---- 6.1 协程对象：调用 async def 函数不会执行 ----
    coro = say_after(0.1, "hello")
    print(f"协程对象类型: {type(coro).__name__}   # coroutine")
    coro.close()        # 不 await 也不 close 会打印 RuntimeWarning: coroutine was never awaited
    # 对比 Java：CompletableFuture.supplyAsync 直接就提交执行了；Python 的协程必须先被调度

    # ---- 6.2 asyncio.run 启动事件循环 ----
    async def one() -> str:
        return await say_after(0.05, "第一个协程")

    print(f"asyncio.run 结果: {asyncio.run(one())}   # 第一个协程")
    # asyncio.run 做三件事：创建事件循环 → 运行协程直到结束 → 关闭事件循环
    # 一个线程只能有一个运行中的事件循环；asyncio.run 内部不能嵌套 asyncio.run

    # ---- 6.3 串行 vs 并发（本节核心证据）----
    serial_cost = asyncio.run(serial_three())
    print(f"串行 3 次 sleep(1): {serial_cost:.2f}s   # 输出示例（约 3.00s）")

    concurrent_cost = asyncio.run(concurrent_three())
    print(f"gather 并发 3 次 sleep(1): {concurrent_cost:.2f}s   # 输出示例（约 1.00s）")
    # 结论：3 个 IO 任务串行 3 秒，并发 1 秒 —— 总耗时 ≈ 最慢的那个。
    # 全程只有 1 个线程，没有创建任何线程/进程，这是 asyncio 最核心的价值。


# ==================== 七、asyncio 常用 API ====================
# ⭐⭐ 常用 —— 经常用
def demo_07_asyncio_api() -> None:
    print("\n=== 七、asyncio 常用 API ===")

    # ---- 7.1 gather：并发执行并收集结果 ----
    async def gather_demo() -> None:
        # Java: CompletableFuture.allOf(f1, f2, f3).join()
        results = await asyncio.gather(
            say_after(0.1, "A"),
            say_after(0.05, "B"),
            say_after(0.02, "C"),
        )
        print(f"gather 结果: {results}   # ['A', 'B', 'C']（顺序与传入顺序一致，不是完成顺序）")

        # return_exceptions=True：异常也当成结果返回，不会让 gather 整个抛出
        # Java: CompletableFuture.allOf 里某个失败会得到 CompletionException
        mixed = await asyncio.gather(
            maybe_fail(1, False),
            maybe_fail(2, True),
            maybe_fail(3, False),
            return_exceptions=True,
        )
        print(f"return_exceptions=True: {mixed[0]} / {type(mixed[1]).__name__}: {mixed[1]} / {mixed[2]}")
        # 任务1成功 / ValueError: 任务2业务失败 / 任务3成功

        # 不加 return_exceptions=True 时，第一个异常会直接抛给 await 处，其余任务继续跑完但不返回结果
        try:
            await asyncio.gather(maybe_fail(1, True), maybe_fail(2, False))
        except ValueError as e:
            print(f"gather 默认行为，异常直接抛出: {e}   # 任务1业务失败")

    asyncio.run(gather_demo())

    # ---- 7.2 create_task：把协程变成任务，立即调度 ----
    async def task_demo() -> None:
        # Java: 没有直接等价物，≈ 手动把任务丢进线程池（但这里是丢进事件循环）
        task = asyncio.create_task(say_after(0.1, "后台任务"))
        print(f"create_task 后任务已开始调度，此刻 done={task.done()}   # False")
        await asyncio.sleep(0.15)       # 干点别的
        print(f"等待后 done={task.done()}   # True")
        print(f"task.result() = {task.result()}   # 后台任务")
        # ⚠️ create_task 的返回值必须被持有，否则可能被 GC 回收导致任务莫名消失

    asyncio.run(task_demo())

    # ---- 7.3 asyncio.sleep：唯一的异步等待方式 ----
    # 绝不能在协程里用 time.sleep（见第八节）
    # asyncio.sleep(0) 是一个「让出控制权」的检查点，≈ Java 的 Thread.yield()

    # ---- 7.4 asyncio.Queue：异步队列，生产者消费者 ----
    # Java: BlockingQueue，但这里的 put/get 是 await 的，不会阻塞线程
    async def queue_demo() -> None:
        q: "asyncio.Queue" = asyncio.Queue(maxsize=5)
        items = [f"消息{i}" for i in range(6)]
        producer_task = asyncio.create_task(async_producer(q, items))
        consumer_tasks = [asyncio.create_task(async_consumer(q, f"异步消费者{i}")) for i in range(2)]
        await producer_task
        counts = await asyncio.gather(*consumer_tasks)
        print(f"两个消费者分别消费: {counts}   # 输出示例（常见 [6, 0]，也可能 [5, 1] 等）")
        # 为什么不是 [3, 3]？单线程协作式调度的经典现象：先被调度的消费者每次都在
        # 队列非空时直接 get 成功（不会让出控制权），另一个被唤醒后消息又被抢走，
        # 只能一直饿着。消息不会重复消费（正确性没问题），但「负载不均」是 asyncio 的常态，
        # 线程池里同样的代码会均分得多 —— 协作式调度必须靠 await 主动让路。

    asyncio.run(queue_demo())

    # ---- 7.5 wait_for：超时控制 ----
    # Java: future.get(1, TimeUnit.SECONDS) → 抛 TimeoutException
    async def timeout_demo() -> None:
        try:
            await asyncio.wait_for(slow_forever(), timeout=0.3)
        except asyncio.TimeoutError:
            print("wait_for 超时: 已取消慢任务   # 输出：wait_for 超时: 已取消慢任务")
        # 正常完成的情况
        value = await asyncio.wait_for(say_after(0.05, "快任务"), timeout=1)
        print(f"wait_for 正常返回: {value}   # 快任务")

    asyncio.run(timeout_demo())

    # ---- 7.6 as_completed：按完成顺序处理 ----
    async def as_completed_demo() -> None:
        tasks = [
            asyncio.create_task(say_after(0.3, "慢")),
            asyncio.create_task(say_after(0.05, "快")),
            asyncio.create_task(say_after(0.15, "中")),
        ]
        print("asyncio.as_completed 按完成顺序:")
        for fut in asyncio.as_completed(tasks):
            print(f"  {await fut}")
        # 输出（顺序不定，由耗时决定）：快 / 中 / 慢

    asyncio.run(as_completed_demo())


# ==================== 八、阻塞陷阱 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
def demo_08_blocking_trap() -> None:
    print("\n=== 八、阻塞陷阱（asyncio 最容易踩的坑）===")

    # ---- 8.1 错误示范：协程里调用 time.sleep ----
    async def wrong() -> None:
        start = time.perf_counter()
        # blocking_task 里是 time.sleep(1)，它不 await，事件循环无法切换任务：
        # quick_task 明明只要 0.1 秒，却要等到阻塞任务彻底跑完才有机会执行。
        _, quick_result = await asyncio.gather(blocking_task(), quick_task(start))
        print(f"错误示范总耗时: {time.perf_counter() - start:.2f}s   # 输出示例（约 1.10s）")
        print(f"错误示范: {quick_result}   # 输出示例（快速任务在演示开始后 1.10s 才完成，被拖慢 10 倍）")

    asyncio.run(wrong())

    # ---- 8.2 正确示范：用 asyncio.sleep ----
    async def right() -> None:
        start = time.perf_counter()
        _, quick_result = await asyncio.gather(non_blocking_task(), quick_task(start))
        print(f"正确示范总耗时: {time.perf_counter() - start:.2f}s   # 输出示例（约 1.00s，两个任务真正重叠）")
        print(f"正确示范: {quick_result}   # 输出示例（快速任务在演示开始后 0.10s 完成，没被拖慢）")

    asyncio.run(right())

    # ---- 8.3 无法避免的阻塞调用怎么办：run_in_executor ----
    async def with_executor() -> str:
        loop = asyncio.get_running_loop()
        # 把阻塞函数丢到线程池里跑，事件循环继续调度其它协程
        # Java: 没有这个问题（虚拟线程阻塞是廉价的），≈ 手动切到另一个线程池
        return await loop.run_in_executor(None, fetch_data, 7, 0.1)

    print(f"run_in_executor 包装阻塞调用: {asyncio.run(with_executor())}   # 任务7完成(耗时0.1s)")
    # 注意：如果被包装的函数是 CPU 密集的（不释放 GIL），丢进线程池也救不了，要用进程池

    # ---- 8.4 对比 Java：这是选型的关键差异 ----
    # Java 21 虚拟线程：阻塞（sleep / JDBC / HTTP）是廉价的，写同步代码就能扛高并发，
    #                   一个阻塞调用只挂起虚拟线程，载体线程会被自动释放去干别的活。
    # Python asyncio  ：阻塞是灾难性的，一个 time.sleep / requests.get 会把「整个事件循环」
    #                   上所有协程全部卡死，且没有任何报错，表现为「服务莫名变慢」。
    # 排查口诀：asyncio 服务变慢 → 先搜代码里有没有 time.sleep / requests / pymysql / open()
    #          这些同步阻塞调用，全部换成异步库（aiohttp / httpx / asyncpg / aiofiles）
    #          或至少用 run_in_executor 包一层。


# ==================== 九、选型指南 ====================
# ⭐⭐⭐ 必会 —— 天天写，不用查文档
def demo_09_choice() -> None:
    print("\n=== 九、选型指南 ===")
    print("CPU 密集（计算、加解密、图片处理）        -> ProcessPoolExecutor / multiprocessing")
    print("IO  密集且量大（爬虫、网关、长连接）      -> asyncio（单线程事件循环，可撑万级并发）")
    print("IO  密集且用同步库（requests/pymysql）    -> ThreadPoolExecutor（改造量最小）")

    # ---------- 决策表（背下来） ----------
    # 场景                       | 首选                  | 备选                | 说明
    # --------------------------|----------------------|--------------------|---------------------------
    # 纯计算，任务重              | ProcessPoolExecutor  | multiprocessing    | 绕过 GIL，进程数=CPU 核数
    # 纯计算，任务轻（<10ms）      | 直接单线程跑          | 无所谓              | 进程/IPC 开销比计算本身还大
    # 大量网络请求（>1000 并发）   | asyncio + aiohttp    | ThreadPoolExecutor | asyncio 内存占用低一个数量级
    # 少量网络请求（<100 并发）    | ThreadPoolExecutor   | asyncio            | 线程池更简单，不用改造成异步
    # 数据库/文件等同步库          | ThreadPoolExecutor   | run_in_executor    | 异步驱动不成熟时最优解
    # 定时任务/后台任务            | asyncio.create_task  | Thread(daemon=True)| 别阻塞事件循环
    #
    # ---------- 对比 Java 的选型 ----------
    # Java 21：虚拟线程可以「一个方案通吃」—— 同步写法 + 虚拟线程既能扛 IO 密集，
    #           CPU 密集丢给 ForkJoinPool / parallelStream 即可，不需要把代码改成异步风格。
    # Python ：没有虚拟线程，异步和同步是两套世界，必须提前选边：
    #           选了 asyncio，全链路（HTTP / DB / Redis / 文件）都必须用异步库，
    #           只要混进一个同步阻塞调用，整套异步架构的性能优势就没了。
    #
    # ---------- 什么时候「不该」用 asyncio ----------
    # 1) 代码里全是同步阻塞库（requests / pymysql / redis-py 同步版），改造成本巨大
    # 2) 团队不熟悉异步调试（栈信息难读、异常容易被吞、"任务从未被 await" 警告）
    # 3) 并发量本来就不高（几百以内），ThreadPoolExecutor 更简单可靠
    # 4) CPU 密集型任务 —— asyncio 对它毫无帮助，反而多一层调度开销


# ==================== 十、实战示例 ====================
# ⭐⭐ 常用 —— 经常用
def demo_10_practice() -> None:
    print("\n=== 十、实战示例 ===")

    # ---- 10.1 asyncio 并发「请求」10 个任务 ----
    async def batch_requests() -> None:
        start = time.perf_counter()
        results = await asyncio.gather(*[fake_request(i) for i in range(10)])
        cost = time.perf_counter() - start
        print(f"并发 10 个请求共耗时: {cost:.2f}s   # 输出示例（约 0.5s = 最慢那个请求的耗时）")
        print(f"前 3 个结果: {results[:3]}   # 输出示例 ['请求0返回', '请求1返回', '请求2返回']")
        # 对比串行版本：10 个请求延迟累加约 0.1~0.5s * 10 ≈ 3 秒
        # 对比 Java：CompletableFuture.allOf(...).thenApply(...) 思路完全一致

    asyncio.run(batch_requests())

    # ---- 10.2 线程池批量处理 + as_completed 收集结果 ----
    def batch_with_threads() -> None:
        tasks = [(i, 0.02 * (i % 5 + 1)) for i in range(12)]
        success = 0
        failed = 0
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=6) as pool:
            future_map = {pool.submit(fetch_data, tid, delay): tid for tid, delay in tasks}
            for fut in as_completed(future_map):
                tid = future_map[fut]
                try:
                    fut.result(timeout=1)
                    success += 1
                except Exception as e:              # 兜底：单个任务失败不影响整批
                    failed += 1
                    print(f"  任务{tid} 失败: {e}")
        cost = time.perf_counter() - start
        print(f"线程池批量处理 12 个任务: 成功 {success} 个，失败 {failed} 个   # 成功 12 个，失败 0 个")
        print(f"总耗时: {cost:.2f}s   # 输出示例（约 0.2s，6 个线程并发）")
        # 对比 Java：ExecutorService.invokeAll(tasks) 或 CompletionService 循环 take()

    batch_with_threads()


# ==================== 主流程 ====================
def main() -> None:
    print('⚠️ 本课会故意触发若干异常用于教学演示，它们都会被 try/except 捕获，控制台出现 Error / Exception 字样属正常现象，脚本退出码为 0\n')

    demo_01_gil()
    demo_02_threading()
    demo_03_race_and_lock()
    demo_04_queue()
    demo_05_executors()
    demo_06_asyncio_basic()
    demo_07_asyncio_api()
    demo_08_blocking_trap()
    demo_09_choice()
    demo_10_practice()

    # ---- daemon 线程被杀演示（本文件最后一个实验）----
    # 主线程即将退出，daemon 线程会被直接杀死，所以下面这行永远不会打印出来。
    def never_printed() -> None:
        time.sleep(3)
        print("  这行永远不会出现：主线程退出时 daemon 线程已被杀死")

    t = threading.Thread(target=never_printed, daemon=True)
    t.start()
    print(f"daemon 线程已启动，主线程不等它。is_alive={t.is_alive()}   # True")
    # 对比 Java：main 方法结束后 JVM 同样只等非 daemon 线程，daemon 线程被直接终止

    print("=== 22 并发与异步 结束 ===")


# ⚠️ 唯一的执行入口：所有逻辑都必须在这里面跑。
# 原因：macOS / Windows 用 spawn 启动子进程，子进程会重新 import 本模块，
#       如果执行逻辑写在顶层（比如顶层直接 print 或直接建进程池），
#       子进程会把顶层代码再跑一遍 → 输出重复，甚至进程无限自我复制（卡死机器）。
if __name__ == "__main__":
    main()
