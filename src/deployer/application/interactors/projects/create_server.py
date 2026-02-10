from deployer.database.identity_provider import IdentityProviderInterface
from deployer.database.repositories.project import ProjectRepository
from deployer.database.transaction import TransactionManagerInterface
from deployer.domain.entities.project import Server
from deployer.domain.exceptions.project import ProjectNotFound
from deployer.domain.exceptions.user import AccessDenied


class CreateServerInteractor:
    def __init__(
        self,
        identity_provider: IdentityProviderInterface,
        transaction_manager: TransactionManagerInterface,
        project_repo: ProjectRepository,
    ):
        self._identity_provider = identity_provider
        self._transaction_manager = transaction_manager
        self._project_repo = project_repo

    async def execute(
        self,
        project_id: int,
        name: str,
        host: str,
        port: int,
        ssh_user: str,
        ssh_secret: str,
        workdir: str,
    ) -> Server:
        user = await self._identity_provider.get_user()
        project = await self._project_repo.get(project_id)
        if not project:
            raise ProjectNotFound
        if project.user_id != user.id:
            raise AccessDenied

        server = Server.create(
            project_id=project_id,
            name=name,
            host=host,
            port=port,
            ssh_user=ssh_user,
            ssh_secret=ssh_secret,
            workdir=workdir,
        )
        server = await self._project_repo.create_server(server)
        await self._transaction_manager.commit()
        return server
