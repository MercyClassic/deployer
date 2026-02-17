from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from deployer.domain.entities.project import Project


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, project: Project) -> None:
        self._session.add(project)

    async def get(self, project_id: int) -> Project | None:
        return await self._session.get(Project, project_id)

    async def delete(self, project: Project) -> None:
        await self._session.delete(project)


    async def get_with_all_data(self, project_id: int) -> Project | None:
        return await self._session.scalar(
            select(Project)
            .where(Project.id == project_id)
            .options(
                joinedload(Project.configs),
                joinedload(Project.servers),
                joinedload(Project.deployments),
            ),
        )

    async def get_by_user_id(self, user_id: int) -> Iterable[Project]:
        return await self._session.scalars(
            select(Project)
            .where(Project.user_id == user_id)
            .options(selectinload(Project.configs), selectinload(Project.servers)),
        )
