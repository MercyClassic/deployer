from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from deployer.domain.entities.deployment import Deployment


class DeploymentRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, deployment: Deployment) -> Deployment:
        self._session.add(deployment)
        return deployment

    async def get(self, deployment_id: int) -> Deployment:
        return await self._session.scalar(
            select(Deployment).where(Deployment.id == deployment_id),
        )

    async def get_history(self, project_id: int) -> Iterable[Deployment]:
        return await self._session.scalars(
            select(Deployment)
            .where(Deployment.project_id == project_id)
            .order_by(Deployment.id.desc()),
        )
