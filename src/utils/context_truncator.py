import tiktoken
from typing import List
from src.api.schema import ChatHistoryItem
from src.core.logger import log
from src.utils.token_utils import token_counter

# --------------------------底层知识点讲解---------------------------
# 1. 滑动窗口核心逻辑
# 固定token容量上限，从最早期消息逐步删除，直到总token低于阈值；
# 优先保留最新对话，符合人类聊天逻辑，不会丢失当前提问上下文；
# 2. token计数原理
# 中文单字≈2token，英文单词≈1token，模型输入长度限制以token为单位而非字符；
# 3. 生产优化点
# 截断时打印淘汰日志，可用于统计用户长对话分布，优化RAG记忆策略
# -------------------------------------------------------------------

# 初始化通义千问兼容编码器
ENCODER = tiktoken.get_encoding("cl100k_base")

def count_text_token(text: str) -> int:
    """计算单段文本占用token数量"""
    tokens = ENCODER.encode(text)
    return len(tokens)

def count_history_total_token(history: List[ChatHistoryItem]) -> int:
    """批量计算整段历史对话总token"""
    total = 0
    for msg in history:
        # role标识也会占用少量token，一并统计
        total += count_text_token(msg.role)
        total += count_text_token(msg.content)
    return total

def sliding_window_truncate(
    history: List[ChatHistoryItem],
    max_total_token: int = 4000
) -> List[ChatHistoryItem]:
    """
    滑动窗口截断历史对话，保证总token不超过上限
    :param history: 原始完整对话历史（正序：最早→最新）
    :param max_total_token: 允许最大token总量
    :return: 裁剪后的对话历史
    """
    # 拷贝数组，不修改原数据
    trunc_history = history.copy()
    total_token = token_counter.count_chat_messages(trunc_history)

    # 循环删除头部最早消息，直到总token达标
    while total_token > max_total_token and len(trunc_history) > 0:
        drop_msg = trunc_history.pop(0)
        log.warning(f"上下文超限，滑动窗口淘汰历史消息：{drop_msg.model_dump()}")
        total_token = token_counter.count_chat_messages(trunc_history)

    log.info(f"滑动窗口截断完成，剩余总token：{total_token}")
    return trunc_history

# 自测脚本
if __name__ == "__main__":
    test_history = [
        ChatHistoryItem(role="user", content="超长文本测试"*1000),
        ChatHistoryItem(role="assistant", content="回复内容"*500),
        ChatHistoryItem(role="user", content="最后提问")
    ]
    res = sliding_window_truncate(test_history, max_total_token=200)
    print("截断后消息条数：", len(res))
