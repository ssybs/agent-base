from src.core.base import BaseLLM
from src.core.settings import settings
from src.core.logger import log
from src.utils.decorators import cost_time
import httpx
from typing import Optional, AsyncGenerator, List
from src.api.schema import ChatHistoryItem
from src.utils.context_truncator import sliding_window_truncate
from src.utils.token_utils import token_counter

# --------------------------知识点分割线---------------------------
# 知识点1：兼容OpenAI标准接口格式
# 通义千问、DeepSeek、Llama本地推理全部兼容OpenAI Body结构，一套代码切换模型
# 知识点2：SSE流式解析逻辑
# 大模型流式返回data:xxx格式，逐行读取，切割片段返回生成器
# 知识点3：httpx异步客户端
# 替代requests同步库，完全async兼容，支持长连接、超时控制
# ----------------------------------------------------------------

class QwenLLM(BaseLLM):
    def __init__(self):
        super().__init__()
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL
        self.model = settings.LLM_MODEL_NAME
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=httpx.Timeout(120)
        )

    def _build_messages(self, prompt: str, history: Optional[List[ChatHistoryItem]], system_prompt: str = None) -> List[dict]:
        """拼接大模型标准messages入参"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt.strip()})
        if history:
            # 自动滑动窗口裁剪，限制总token4000
            safe_history = sliding_window_truncate(history, max_total_token=4000)
            # 统计截断后token，打印日志
            history_token = token_counter.count_chat_messages(safe_history)
            prompt_token = token_counter.count_single_text(prompt)
            total_input_token = history_token + prompt_token
            log.info(f"输入token统计：历史对话{history_token}，当前提问{prompt_token}，合计{total_input_token}")
            for item in safe_history:
                messages.append({"role": item.role, "content": item.content})
        messages.append({"role": "user", "content": prompt})
        return messages

    @cost_time
    async def chat(self, prompt: str, history: Optional[List[ChatHistoryItem]] = None, system_prompt: str = None) -> str:
        """一次性完整返回对话结果"""
        url = f"{self.base_url}/chat/completions"
        req_body = {
            "model": self.model,
            "messages": self._build_messages(prompt, history, system_prompt),
            "stream": False
        }
        resp = await self.client.post(url, json=req_body)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return content

    async def stream_chat(self, prompt: str, history: Optional[List[ChatHistoryItem]] = None, system_prompt: str = None) -> AsyncGenerator[str, None]:
        """流式对话生成器，逐段返回文本"""
        url = f"{self.base_url}/chat/completions"
        req_body = {
            "model": self.model,
            "messages": self._build_messages(prompt, history, system_prompt),
            "stream": True
        }
        async with self.client.stream("POST", url, json=req_body) as stream_resp:
            async for line in stream_resp.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                data_str = line.removeprefix("data: ").strip()
                if data_str == "[DONE]":
                    return
                import json
                chunk = json.loads(data_str)
                delta = chunk["choices"][0]["delta"].get("content", "")
                if delta:
                    yield delta
