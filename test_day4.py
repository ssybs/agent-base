from src.utils.token_utils import token_counter
from src.api.schema import ChatHistoryItem
from src.utils.context_truncator import sliding_window_truncate
import asyncio
from src.llm.qwen_llm import QwenLLM

async def main():
    print("==== Day4 Token工具 & LLM底层自测 ====")
    # 1. 纯文本token计数测试
    test_text = "AI Agent 是具备自主规划、工具调用、记忆能力的智能体，RAG检索增强可以减少大模型幻觉"
    text_token = token_counter.count_single_text(test_text)
    print(f"文本token数量：{text_token}")

    # 2. 多轮对话token统计
    test_history = [
        ChatHistoryItem(role="user", content="什么是Transformer？"),
        ChatHistoryItem(role="assistant", content="Transformer基于自注意力机制，分为Encoder和Decoder两类..."),
        ChatHistoryItem(role="user", content="Encoder和Decoder分别适合什么场景？")
    ]
    history_total = token_counter.count_chat_messages(test_history)
    print(f"多轮对话总token：{history_total}")
    print(f"是否超限：{token_counter.is_over_limit(test_history, max_token=2000)}")

    # 3. 超长对话截断测试
    long_msg = ChatHistoryItem(role="user", content="超长测试文本" * 3000)
    long_history = [long_msg]
    safe_hist = sliding_window_truncate(long_history, max_total_token=500)
    print(f"超长对话截断后消息数：{len(safe_hist)}")

    # 4. 完整LLM调用，查看token日志打印
    llm = QwenLLM()
    resp = await llm.chat(prompt="简单讲一下大模型上下文窗口限制", history=test_history)
    print(f"模型返回片段：{resp[:150]}")

if __name__ == "__main__":
    asyncio.run(main())
