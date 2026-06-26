from src.core.logger import log
from src.core.base import BaseLLM
from src.utils.async_utils import demo_async_test
from src.utils.decorators import cost_time
import asyncio

# 测试抽象LLM子类
class TestLLM(BaseLLM):
    @cost_time
    async def chat(self, prompt: str, history=None):
        await asyncio.sleep(0.5)
        return f"测试回复：{prompt}"

    async def stream_chat(self, prompt: str, history=None):
        yield "片段1"
        await asyncio.sleep(0.2)
        yield "片段2"

async def main():
    log.info("===== Day1 自测开始 =====")
    llm = TestLLM()
    res = await llm.chat("你好Agent")
    log.info(res)
    await demo_async_test()
    log.info("===== Day1 自测完成 =====")

if __name__ == "__main__":
    asyncio.run(main())
