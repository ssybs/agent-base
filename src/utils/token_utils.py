import tiktoken
from typing import List, Optional
from src.api.schema import ChatHistoryItem
from src.core.logger import log
from src.core.settings import settings

# --------------------------知识点分割线---------------------------
# 1. cl100k_base 编码：OpenAI/通义千问/Qwen统一兼容分词器
# 2. 统一封装工具类，全局单例，避免重复初始化编码器
# 3. 区分纯文本计数、完整对话消息计数（role标识也会消耗token）
# 4. 内置窗口校验方法，直接对接Day3滑动窗口截断逻辑
# ----------------------------------------------------------------

class TokenCounter:
    """全局统一Token计数工具单例"""
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 初始化分词器
            cls._instance.encoder = tiktoken.get_encoding("cl100k_base")
            log.info("TokenCounter 分词器初始化完成")
        return cls._instance

    def count_single_text(self, text: str) -> int:
        """统计单段纯文本token数量"""
        if not text:
            return 0
        token_ids = self.encoder.encode(text)
        return len(token_ids)

    def count_chat_messages(self, history: Optional[List[ChatHistoryItem]]) -> int:
        """统计整组对话历史总token（包含role标记）"""
        if not history:
            return 0
        total = 0
        for msg in history:
            total += self.count_single_text(msg.role)
            total += self.count_single_text(msg.content)
        return total

    def is_over_limit(self, history: List[ChatHistoryItem], max_token: int = 4000) -> bool:
        """判断对话是否超出token上限"""
        total = self.count_chat_messages(history)
        if total > max_token:
            log.warning(f"对话总token {total} 超过阈值 {max_token}，需要滑动窗口截断")
            return True
        return False

# 全局导出单例，项目各处直接调用
token_counter = TokenCounter()
