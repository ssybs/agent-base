from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from src.core.logger import log

# --------------------------知识点分割线---------------------------
# 知识点1：ABC抽象基类作用
# 定义统一规范接口，所有工具、LLM、记忆模块必须继承并实现方法
# 优势：低耦合、方便替换底层实现（比如切换通义千问/OpenAI模型不用改上层业务）
# 知识点2：@abstractmethod强制实现
# 子类不实现该方法直接运行会抛出异常，避免漏写核心逻辑
# 知识点3：统一error捕获父类方法
# 所有子类自动继承异常捕获逻辑，减少重复try-except代码
# ----------------------------------------------------------------

class BaseModule(ABC):
    """所有Agent模块顶层抽象父类"""
    def __init__(self):
        self.module_name = self.__class__.__name__
        log.info(f"初始化模块: {self.module_name}")

    async def safe_run(self, func, *args, **kwargs) -> Any:
        """统一异常捕获封装，所有模块执行函数统一走这个方法"""
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            log.error(f"【{self.module_name}】执行失败: {str(e)}", exc_info=True)
            raise e

class BaseLLM(BaseModule):
    """大模型统一抽象接口"""
    @abstractmethod
    async def chat(self, prompt: str, history: Optional[list] = None) -> str:
        """普通对话，一次性返回完整结果"""
        ...

    @abstractmethod
    async def stream_chat(self, prompt: str, history: Optional[list] = None):
        """流式对话，生成器逐段返回（SSE打字机效果）"""
        ...

class BaseTool(BaseModule):
    """Agent工具统一抽象接口（计算器、数据库查询等）"""
    @abstractmethod
    async def run(self, params: Dict[str, Any]) -> str:
        """执行工具能力，入参结构化字典"""
        ...

    @abstractmethod
    def get_tool_desc(self) -> Dict[str, Any]:
        """返回工具描述JSON，用于Function Calling函数定义"""
        ...
