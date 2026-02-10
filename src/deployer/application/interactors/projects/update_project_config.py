from deployer.database.identity_provider import IdentityProviderInterface
from deployer.database.repositories.project import ProjectRepository
from deployer.database.transaction import TransactionManagerInterface
from deployer.domain.entities.project import ProjectConfig
from deployer.domain.exceptions.project import ActiveConfigNotFound, ProjectNotFound
from deployer.domain.exceptions.user import AccessDenied


class UpdateProjectConfigInteractor:
    def __init__(
        self,
        identity_provider: IdentityProviderInterface,
        transaction_manager: TransactionManagerInterface,
        project_repo: ProjectRepository,
    ):
        self._identity_provider = identity_provider
        self._transaction_manager = transaction_manager
        self._project_repo = project_repo

    async def execute(self, project_id: int, config: dict) -> ProjectConfig:
        user = await self._identity_provider.get_user()
        project = await self._project_repo.get_with_all_data(project_id)
        if not project:
            raise ProjectNotFound
        if project.user_id != user.id:
            raise AccessDenied

        try:
            current_config = project.active_config
        except ActiveConfigNotFound:
            next_version = 1
        else:
            current_config.set_inactive()
            next_version = current_config.version + 1

        new_config = ProjectConfig.create(
            project_id=project_id,
            version=next_version,
            config=config,
            strategy=project.deploy_strategy,
        )
        config = await self._project_repo.create_config(new_config)

        await self._transaction_manager.commit()
        return config
