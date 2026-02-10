from deployer.database.identity_provider import IdentityProviderInterface
from deployer.database.repositories.project import ProjectRepository
from deployer.database.transaction import TransactionManagerInterface
from deployer.domain.entities.project import Project


class CreateProjectInteractor:
    def __init__(
        self,
        identity_provider: IdentityProviderInterface,
        transaction_manager: TransactionManagerInterface,
        project_repo: ProjectRepository,
    ):
        self._identity_provider = identity_provider
        self._transaction_manager = transaction_manager
        self._project_repo = project_repo

    async def execute(self, name: str, deploy_strategy: str) -> Project:
        user = await self._identity_provider.get_user()
        project = Project.create(
            user_id=user.id,
            name=name,
            deploy_strategy=deploy_strategy,
        )
        await self._project_repo.create(project)
        await self._transaction_manager.commit()
        return project
