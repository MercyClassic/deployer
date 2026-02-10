from deployer.database.identity_provider import IdentityProviderInterface
from deployer.database.repositories.project import ProjectRepository
from deployer.database.transaction import TransactionManagerInterface
from deployer.domain.entities.project import ProjectConfig
from deployer.domain.exceptions.project import ImpossibleProjectConfigVersion
from deployer.domain.exceptions.user import AccessDenied


class RollbackProjectConfigInteractor:
    def __init__(
        self,
        identity_provider: IdentityProviderInterface,
        transaction_manager: TransactionManagerInterface,
        project_repo: ProjectRepository,
    ):
        self._identity_provider = identity_provider
        self._transaction_manager = transaction_manager
        self._project_repo = project_repo

    async def execute(self, project_id: int, version: int) -> ProjectConfig:
        user = await self._identity_provider.get_user()
        project = await self._project_repo.get_with_all_data(project_id)
        if project.user_id != user.id:
            raise AccessDenied

        if version < 1:
            raise ImpossibleProjectConfigVersion

        config = await self._project_repo.get_config_by_version(
            project_id, version, project.deploy_strategy,
        )
        if not config or project.active_config.version == version:
            raise ImpossibleProjectConfigVersion

        await self._project_repo.delete_configs_after_version(
            project_id, version, project.deploy_strategy,
        )
        config.set_active()

        await self._transaction_manager.commit()
        return config
