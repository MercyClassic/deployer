import os
from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from deployer.database.repositories.deployment import DeploymentRepository
from deployer.database.repositories.project import ProjectRepository
from deployer.database.repositories.user import UserRepository
from deployer.database.transaction import (
    TransactionManager,
    TransactionManagerInterface,
)


class DbProvider(Provider):
    scope = Scope.REQUEST
    component = 'db'

    @provide(scope=Scope.APP)
    async def get_async_session_maker(
        self,
    ) -> async_sessionmaker[AsyncSession]:
        engine = create_async_engine(
            os.environ['DB_URI'],
            isolation_level='REPEATABLE READ',
        )
        return async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @provide
    async def get_async_session(
        self,
        async_session_maker: async_sessionmaker[AsyncSession],
    ) -> AsyncGenerator[AsyncSession, None]:
        async with async_session_maker() as session:
            yield session

    @provide
    async def get_transaction_manager(
        self,
        session: AsyncSession,
    ) -> TransactionManagerInterface:
        return TransactionManager(session)

    @provide
    async def get_deployment_repository(
        self,
        session: AsyncSession,
    ) -> DeploymentRepository:
        return DeploymentRepository(session)

    @provide
    async def get_project_repository(
        self,
        session: AsyncSession,
    ) -> ProjectRepository:
        return ProjectRepository(session)

    @provide
    async def get_user_repository(
        self,
        session: AsyncSession,
    ) -> UserRepository:
        return UserRepository(session)
