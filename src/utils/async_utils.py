import asyncio
from typing import Coroutine, List
from src.core.logger import log

# --------------------------知识点分割线---------------------------
# 知识点1：协程、线程、进程区分
# 协程(async/await)：IO密集型（网络请求、数据库、大模型调用），单线程切换无开销
# 线程：阻塞同步IO（老旧数据库驱动），GIL限制CPU计算
# 进程：CPU密集计算，多核心并行，开销最大
# Agent场景90%都是IO密集，优先使用async协程
# 知识点2：asyncio.gather 并发执行
# 同时发起多个LLM请求/文档处理，大幅提升吞吐量，等待全部任务完成再返回
# 知识点3：异常捕获并发任务
# return_exceptions=True 防止单个任务失败导致全部并发崩溃
# ----------------------------------------------------------------

async def batch_run_tasks(coro_list: List[Coroutine], limit: int = 5):
    """
    批量异步执行任务，限制并发数量，防止瞬间打满模型接口限流
    :param coro_list: 协程任务列表
    :param limit: 最大并发数
    :return: 所有任务执行结果列表
    """
    semaphore = asyncio.Semaphore(limit)

    async def wrap_task(coro):
        async with semaphore:
            try:
                return await coro
            except Exception as e:
                log.error(f"批量任务执行异常: {str(e)}")
                return None

    wrap_coros = [wrap_task(coro) for coro in coro_list]
    results = await asyncio.gather(*wrap_coros)
    return results

# 简易测试入口（Day1自测用）
async def demo_async_test():
    async def mock_llm_call(name: str):
        log.info(f"开始调用模型 {name}")
        await asyncio.sleep(1)
        return f"{name} 调用完成"

    tasks = [mock_llm_call(f"模型-{i}") for i in range(8)]
    res = await batch_run_tasks(tasks, limit=3)
    log.info(f"批量执行结果: {res}")

if __name__ == "__main__":
    asyncio.run(demo_async_test())
