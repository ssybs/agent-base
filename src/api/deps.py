from fastapi import Depends, HTTPException, Header
from src.core.settings import settings
from src.llm.qwen_llm import QwenLLM
from typing import Annotated
from src.core.db import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

# --------------------------知识点分割线---------------------------
# 知识点1：Depends依赖注入
# 统一创建全局资源（LLM客户端、数据库连接），复用实例，不用每次请求新建
# Annotated 简化类型注解写法，分离类型与依赖逻辑
# 知识点2：接口鉴权
# 简易token鉴权，企业生产替换为JWT/OAuth2
# 知识点3：request_id 链路追踪
# 每个请求生成唯一uuid，传递给日志、LLM调用，出现问题一键全链路检索
# ----------------------------------------------------------------

# 全局大模型单例（全局复用，避免重复初始化HTTP客户端）
global_llm = QwenLLM()

async def get_request_id(x_request_id: str | None = Header(None)) -> str:
    if not x_request_id:
        x_request_id = str(uuid.uuid4())
    return x_request_id

async def verify_token(x_token: Annotated[str, Header()]):
    """简易接口鉴权依赖，所有接口强制携带Token"""
    # 生产环境替换为数据库查询有效token
    if not x_token or len(x_token) < 8:
        raise HTTPException(status_code=401, detail="Token 无效，请鉴权后访问")
    return x_token

# 通用依赖组合：鉴权 + 请求ID
# CommonDep = Annotated[tuple[str, str], Depends(lambda: (verify_token, get_request_id))]

# 拆分两个独立依赖，不要合并tuple
TokenDep = Annotated[str, Depends(verify_token)]
RequestIdDep = Annotated[str, Depends(get_request_id)]
# 新增数据库依赖注解
DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]

# 获取全局LLM实例依赖
def get_llm_client():
    return global_llm
