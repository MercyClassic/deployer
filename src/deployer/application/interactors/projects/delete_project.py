from deployer.database.identity_provider import IdentityProviderInterface
from deployer.database.repositories.project import ProjectRepository
from deployer.database.transaction import TransactionManagerInterface


class DeleteProjectInteractor:
    def __init__(
        self,
        identity_provider: IdentityProviderInterface,
        transaction_manager: TransactionManagerInterface,
        project_repo: ProjectRepository,
    ):
        self._identity_provider = identity_provider
        self._transaction_manager = transaction_manager
        self._project_repo = project_repo

    async def execute(self, project_id: int) -> None:
        user = await self._identity_provider.get_user()
        project = await self._project_repo.get_with_all_data(project_id)
        project.check_user_permitted(user.id)
        await self._project_repo.delete(project)
        await self._transaction_manager.commit()
