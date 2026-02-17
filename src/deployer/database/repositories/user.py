from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from deployer.domain.entities.project import Project
from deployer.domain.entities.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, user: User) -> None:
        self._session.add(user)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        return await self._session.scalar(
            select(User).where(User.telegram_id == telegram_id),
        )

    async def get_all_projects(self, user: User) -> Iterable[Project]:
        return await self._session.scalars(
            select(Project).where(Project.user_id == user.id),
        )
