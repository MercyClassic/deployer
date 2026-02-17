from deployer.database.identity_provider import IdentityProviderInterface
from deployer.database.repositories.project import ProjectRepository
from deployer.domain.entities.project import Project
from deployer.domain.exceptions.project import ProjectNotFound


class GetProjectInfoInteractor:
    def __init__(
        self,
        identity_provider: IdentityProviderInterface,
        project_repo: ProjectRepository,
    ):
        self._identity_provider = identity_provider
        self._project_repo = project_repo

    async def execute(self, project_id: int) -> Project:
        user = await self._identity_provider.get_user()
        project = await self._project_repo.get_with_all_data(project_id)
        if not project:
            raise ProjectNotFound
        project.check_user_permitted(user.id)
        return project
