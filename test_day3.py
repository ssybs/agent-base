from src.utils.memory_queue import SessionMemoryQueue
from src.utils.context_truncator import count_text_token, sliding_window_truncate
from src.api.schema import ChatHistoryItem
import asyncio
from src.llm.qwen_llm import QwenLLM

async def main():
    print("==== Day3 算法工具自测 ====")
    # 1. 测试会话记忆队列自动淘汰
    mem = SessionMemoryQueue(max_msg_count=4)
    mem.add_msg("user", "第一轮提问")
    mem.add_msg("assistant", "第一轮回答")
    mem.add_msg("user", "第二轮提问")
    mem.add_msg("assistant", "第二轮回答")
    mem.add_msg("user", "第三轮提问")
    print("队列自动淘汰后历史：", mem.get_all_history())

    # 2. 测试滑动窗口超长截断
    long_history = [ChatHistoryItem(role="user", content="超长上下文"*2000)]
    safe_history = sliding_window_truncate(long_history, max_total_token=300)
    print("截断后消息长度：", len(safe_history))

    # 3. 测试集成LLM自动截断对话
    llm = QwenLLM()
    test_hist = [ChatHistoryItem(role="user", content="重复超长文本"*3000)]
    resp = await llm.chat(prompt="总结上面内容", history=test_hist)
    print("模型返回结果：", resp[:100])

if __name__ == "__main__":
    asyncio.run(main())
