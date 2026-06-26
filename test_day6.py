import asyncio
from src.core.db import AsyncSessionLocal, init_db_tables
from src.db import crud

async def test_db_crud():
    # Initialize database tables
    await init_db_tables()
    # Create a database session
    async with AsyncSessionLocal() as db:
        test_token = "test_token_123456"
        # Create or retrieve the user
        user = await crud.get_user_by_token(db, test_token)
        if not user:
            user = await crud.create_user(db, test_token)
        print(f"用户ID: {user.id}")
        # Create a chat session
        session = await crud.create_chat_session(db, user.id, "测试会话")
        print(f"新建会话ID: {session.id}")
        # Write chat messages
        await crud.add_chat_message(db, session.id, "user", "什么是Docker？")
        await crud.add_chat_message(db, session.id, "assistant", "Docker是容器化部署工具，统一运行环境。")
        # Query history
        history = await crud.get_session_history(db, session.id)
        print("会话历史记录：")
        for msg in history:
            print(f"{msg.role}: {msg.content}")

if __name__ == "__main__":
    asyncio.run(test_db_crud())
