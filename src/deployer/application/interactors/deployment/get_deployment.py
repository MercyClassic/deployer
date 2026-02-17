from deployer.database.identity_provider import IdentityProviderInterface
from deployer.database.repositories.deployment import DeploymentRepository
from deployer.database.repositories.project import ProjectRepository
from deployer.domain.entities.deployment import Deployment
from deployer.domain.exceptions.deployment import DeploymentNotFound
from deployer.domain.exceptions.project import ProjectNotFound


class GetDeploymentInteractor:
    def __init__(
        self,
        identity_provider: IdentityProviderInterface,
        project_repo: ProjectRepository,
        deployment_repo: DeploymentRepository,
    ):
        self._identity_provider = identity_provider
        self._project_repo = project_repo
        self._deployment_repo = deployment_repo

    async def execute(self, deployment_id: int) -> Deployment:
        user = await self._identity_provider.get_user()
        deployment = await self._deployment_repo.get(deployment_id)
        if not deployment:
            raise DeploymentNotFound
        project = await self._project_repo.get(deployment.project_id)
        if not project:
            raise ProjectNotFound
        project.check_user_permitted(user.id)
        return deployment
