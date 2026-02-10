from deployer.database.identity_provider import IdentityProviderInterface
from deployer.database.repositories.project import ProjectRepository
from deployer.database.transaction import TransactionManagerInterface
from deployer.domain.exceptions.user import AccessDenied


class DeleteServerInteractor:
    def __init__(
        self,
        identity_provider: IdentityProviderInterface,
        transaction_manager: TransactionManagerInterface,
        project_repo: ProjectRepository,
    ):
        self._identity_provider = identity_provider
        self._transaction_manager = transaction_manager
        self._project_repo = project_repo

    async def execute(self, server_id: int) -> None:
        user = await self._identity_provider.get_user()
        server = await self._project_repo.get_server(server_id)
        project = await self._project_repo.get(server.project_id)
        if project.user_id != user.id:
            raise AccessDenied

        await self._project_repo.delete_server(server)
        await self._transaction_manager.commit()
