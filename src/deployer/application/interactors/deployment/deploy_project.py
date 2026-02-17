from deployer.application.deployers.docker import DockerDeployer
from deployer.application.deployers.execute import execute_deploy
from deployer.application.deployers.git import GitDeployer
from deployer.application.deployers.shell import ShellDeployer
from deployer.database.identity_provider import IdentityProviderInterface
from deployer.database.repositories.deployment import DeploymentRepository
from deployer.database.repositories.project import ProjectRepository
from deployer.database.transaction import TransactionManagerInterface
from deployer.domain.entities.deployment import Deployment, DeploymentStatus
from deployer.domain.entities.project import DeployStrategy
from deployer.domain.exceptions.deployment import UnsupportedStrategy
from deployer.domain.exceptions.project import ProjectNotFound
from deployer.domain.exceptions.user import AccessDenied


class DeployProjectInteractor:
    def __init__(
        self,
        transaction_manager: TransactionManagerInterface,
        identity_provider: IdentityProviderInterface,
        project_repo: ProjectRepository,
        deployment_repo: DeploymentRepository,
    ):
        self._transaction_manager = transaction_manager
        self._identity_provider = identity_provider
        self._project_repo = project_repo
        self._deployment_repo = deployment_repo

    async def execute(self, project_id: int) -> Deployment:
        user = await self._identity_provider.get_user()
        project = await self._project_repo.get_with_all_data(project_id)
        if not project:
            raise ProjectNotFound
        if project.user_id != user.id:
            raise AccessDenied
        project.check_deploy_possible()

        deployer_mapper = {
            DeployStrategy.shell: ShellDeployer,
            DeployStrategy.git: GitDeployer,
            DeployStrategy.docker: DockerDeployer,
        }
        try:
            deployer_cls = deployer_mapper[project.deploy_strategy]
        except KeyError:
            raise UnsupportedStrategy

        deployment = Deployment.create(
            project_id=project_id,
            status=DeploymentStatus.pending,
        )
        await self._deployment_repo.create(deployment)
        await self._transaction_manager.flush()

        execute_deploy(
            deployer_cls,
            deployment.id,
            project.active_config.config,
            project.servers,
        )

        await self._transaction_manager.commit()
        return deployment
