from collections import deque
from typing import List
from src.api.schema import ChatHistoryItem
from src.core.logger import log

# --------------------------底层知识点讲解---------------------------
# 1. collections.deque 双端队列底层
# list.pop(0) 删除头部元素需要整体后移，时间复杂度 O(N)；
# deque 是双向链表实现，popleft() O(1)，海量对话消息性能差距极大；
# 2. FIFO先进先出淘汰策略
# 新消息追加队尾，超出最大条数时，自动删除队头最早历史消息；
# 3. 业务场景：单用户会话内存缓存，减少频繁读写数据库压力
# -------------------------------------------------------------------

class SessionMemoryQueue:
    """单会话短期内存记忆队列，自动淘汰老旧对话"""
    def __init__(self, max_msg_count: int = 20):
        # 最大保存消息条数，超过自动淘汰最早消息
        self.max_msg_count = max_msg_count
        # 存储 ChatHistoryItem 对话消息
        self.queue: deque[ChatHistoryItem] = deque()

    def add_msg(self, role: str, content: str):
        """新增一条对话消息，自动判断是否超出上限并淘汰旧消息"""
        item = ChatHistoryItem(role=role, content=content)
        self.queue.append(item)
        log.debug(f"新增会话消息，当前消息总量：{len(self.queue)}")
        # 超出最大条数，循环删除队头最早消息
        while len(self.queue) > self.max_msg_count:
            drop_item = self.queue.popleft()
            log.warning(f"会话消息超限，自动淘汰历史消息：{drop_item.model_dump()}")

    def get_all_history(self) -> List[ChatHistoryItem]:
        """获取完整历史对话列表，按时间正序（最早→最新）"""
        return list(self.queue)

    def clear(self):
        """清空当前会话所有记忆"""
        self.queue.clear()
        log.info("清空会话全部记忆")

# 自测代码
if __name__ == "__main__":
    memory = SessionMemoryQueue(max_msg_count=3)
    memory.add_msg("user", "问题1")
    memory.add_msg("assistant", "回答1")
    memory.add_msg("user", "问题2")
    memory.add_msg("assistant", "回答2")
    memory.add_msg("user", "问题3")
    print("最终保留历史：", memory.get_all_history())
