from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import TokenDep, DBSessionDep
from src.db import crud
from src.core.logger import log

router = APIRouter(prefix="/history", tags=["对话历史管理"])

@router.get("/{session_id}")
async def get_chat_history(
    session_id: int,
    token: TokenDep,
    db: DBSessionDep
):
    """根据会话ID读取全部历史对话"""
    # 校验用户
    user = await crud.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    # 校验会话归属
    session = await crud.get_session_by_id(db, session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    history = await crud.get_session_history(db, session_id)
    return {"session_id": session_id, "history": history}
