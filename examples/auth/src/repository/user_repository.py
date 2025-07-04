from src.entity.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_username(self, username: str):
        q = select(User).where(User.username == username)
        result = await self.session.execute(q)

        return result.scalars().first()

    async def create_user(self, username: str, email: str, password_hash: str):
        user = User(username=username, email=email, password_hash=password_hash)

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user
