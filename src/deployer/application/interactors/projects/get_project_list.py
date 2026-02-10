from collections.abc import Iterable

from deployer.database.identity_provider import IdentityProviderInterface
from deployer.database.repositories.project import ProjectRepository
from deployer.domain.entities.project import Project


class GetProjectListInteractor:
    def __init__(
        self,
        identity_provider: IdentityProviderInterface,
        project_repo: ProjectRepository,
    ):
        self._identity_provider = identity_provider
        self._project_repo = project_repo

    async def execute(self) -> Iterable[Project]:
        user = await self._identity_provider.get_user()
        projects = await self._project_repo.get_by_user_id(user.id)
        return projects
