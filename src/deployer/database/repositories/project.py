from collections.abc import Iterable

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from deployer.domain.entities.project import (
    DeployStrategy,
    Project,
    ProjectConfig,
    Server,
)


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    # project
    async def create(self, project: Project) -> Project:
        self._session.add(project)
        return project

    async def delete(self, project: Project) -> None:
        await self._session.delete(project)

    async def get(self, project_id: int) -> Project | None:
        return await self._session.scalar(
            select(Project).where(Project.id == project_id),
        )

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

    # server
    async def create_server(self, server: Server) -> Server:
        self._session.add(server)
        return server

    async def delete_server(self, server: Server) -> None:
        await self._session.delete(server)

    async def get_server(self, server_id: int) -> Server | None:
        return await self._session.scalar(
            select(Server).where(Server.id == server_id),
        )

    # config
    async def create_config(self, config: ProjectConfig) -> ProjectConfig:
        self._session.add(config)
        return config

    async def get_config_by_version(
        self,
        project_id: int,
        version: int,
        strategy: DeployStrategy,
    ) -> ProjectConfig | None:
        return await self._session.scalar(
            select(ProjectConfig).where(
                ProjectConfig.project_id == project_id,
                ProjectConfig.version == version,
                ProjectConfig.strategy == strategy,
            ),
        )

    async def delete_configs_after_version(
        self,
        project_id: int,
        version: int,
        strategy: DeployStrategy,
    ) -> None:
        await self._session.execute(
            delete(ProjectConfig).where(
                ProjectConfig.project_id == project_id,
                ProjectConfig.version > version,
                ProjectConfig.strategy == strategy,
            ),
        )
