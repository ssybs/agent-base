from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# --------------------------知识点分割线---------------------------
# 知识点1：Pydantic v2核心能力
# 自动类型校验、自动错误提示、模型转JSON、嵌套结构体解析
# Function Calling必须依靠Pydantic解析模型返回的结构化JSON
# Field用于参数描述、默认值、长度限制，接口文档自动生成说明
# 知识点2：区分入参/出参模型
# ChatRequest：前端提交请求校验
# ChatStreamResponse：流式返回单片段结构
# ----------------------------------------------------------------

class ChatHistoryItem(BaseModel):
    role: str = Field(description="角色 user / assistant")
    content: str = Field(description="对话内容")

class ChatRequest(BaseModel):
    prompt: str = Field(description="用户当前提问", min_length=1)
    history: Optional[List[ChatHistoryItem]] = Field(default=[], description="历史多轮对话")
    stream: bool = Field(default=True, description="是否开启流式输出")

class ChatStreamResponse(BaseModel):
    content: str
    finish: bool = Field(description="是否对话结束")
