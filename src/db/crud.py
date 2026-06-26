from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import User, ChatSession, ChatMessage
from src.api.schema import ChatHistoryItem
from src.core.logger import log

# ===================== User 用户操作 =====================
async def get_user_by_token(db: AsyncSession, token: str) -> Optional[User]:
    stmt = select(User).where(User.token == token)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, token: str) -> User:
    user = User(token=token)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    log.info(f"新建用户，token:{token}")
    return user

# ===================== 会话操作 =====================
async def create_chat_session(db: AsyncSession, user_id: int, session_name: str = "默认会话") -> ChatSession:
    session = ChatSession(user_id=user_id, session_name=session_name)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

async def get_session_by_id(db: AsyncSession, session_id: int, user_id: int) -> Optional[ChatSession]:
    stmt = select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()

# ===================== 对话消息操作 =====================
async def add_chat_message(db: AsyncSession, session_id: int, role: str, content: str) -> ChatMessage:
    msg = ChatMessage(session_id=session_id, role=role, content=content)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg

async def get_session_history(db: AsyncSession, session_id: int) -> List[ChatHistoryItem]:
    """读取会话全部历史，转为接口标准ChatHistoryItem格式"""
    stmt = select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.id)
    result = await db.execute(stmt)
    msg_list = result.scalars().all()
    history = [ChatHistoryItem(role=m.role, content=m.content) for m in msg_list]
    return history
