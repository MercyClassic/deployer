from typing import Annotated

from dishka import FromComponent, Provider, Scope, provide

from deployer.application.interactors.deployment.deploy_project import (
    DeployProjectInteractor,
)
from deployer.application.interactors.deployment.get_deploy_history import (
    GetDeployHistoryInteractor,
)
from deployer.application.interactors.deployment.get_deployment import (
    GetDeploymentInteractor,
)
from deployer.application.interactors.projects.create_project import (
    CreateProjectInteractor,
)
from deployer.application.interactors.projects.create_server import (
    CreateServerInteractor,
)
from deployer.application.interactors.projects.delete_project import (
    DeleteProjectInteractor,
)
from deployer.application.interactors.projects.delete_server import (
    DeleteServerInteractor,
)
from deployer.application.interactors.projects.get_project_info import (
    GetProjectInfoInteractor,
)
from deployer.application.interactors.projects.get_project_list import (
    GetProjectListInteractor,
)
from deployer.application.interactors.projects.rollback_project_config import (
    RollbackProjectConfigInteractor,
)
from deployer.application.interactors.projects.show_project_config import (
    ShowProjectConfigInteractor,
)
from deployer.application.interactors.projects.update_project_config import (
    UpdateProjectConfigInteractor,
)
from deployer.application.interactors.projects.update_project_strategy import (
    UpdateProjectStrategyInteractor,
)
from deployer.application.interactors.user.create_user import CreateUserInteractor
from deployer.database.identity_provider import IdentityProviderInterface
from deployer.database.repositories.deployment import DeploymentRepository
from deployer.database.repositories.project import ProjectRepository
from deployer.database.repositories.user import UserRepository
from deployer.database.transaction import TransactionManagerInterface


class InteractorProvider(Provider):
    scope = Scope.REQUEST
    DB_COMPONENT = 'db'
    IDENTITY_COMPONENT = 'identity'

    @provide
    async def provide_create_user_interactor(
        self,
        transaction_manager: Annotated[
            TransactionManagerInterface, FromComponent(DB_COMPONENT),
        ],
        user_repo: Annotated[UserRepository, FromComponent(DB_COMPONENT)],
    ) -> CreateUserInteractor:
        return CreateUserInteractor(transaction_manager, user_repo)

    @provide
    async def provide_create_project_interactor(
        self,
        transaction_manager: Annotated[
            TransactionManagerInterface, FromComponent(DB_COMPONENT),
        ],
        identity_provider: Annotated[
            IdentityProviderInterface, FromComponent(IDENTITY_COMPONENT),
        ],
        project_repo: Annotated[ProjectRepository, FromComponent(DB_COMPONENT)],
    ) -> CreateProjectInteractor:
        return CreateProjectInteractor(
            identity_provider, transaction_manager, project_repo,
        )

    @provide
    async def provide_update_project_strategy_interactor(
        self,
        transaction_manager: Annotated[
            TransactionManagerInterface, FromComponent(DB_COMPONENT),
        ],
        identity_provider: Annotated[
            IdentityProviderInterface, FromComponent(IDENTITY_COMPONENT),
        ],
        project_repo: Annotated[ProjectRepository, FromComponent(DB_COMPONENT)],
    ) -> UpdateProjectStrategyInteractor:
        return UpdateProjectStrategyInteractor(
            identity_provider, transaction_manager, project_repo,
        )

    @provide
    async def provide_create_server_interactor(
        self,
        transaction_manager: Annotated[
            TransactionManagerInterface, FromComponent(DB_COMPONENT),
        ],
        identity_provider: Annotated[
            IdentityProviderInterface, FromComponent(IDENTITY_COMPONENT),
        ],
        project_repo: Annotated[ProjectRepository, FromComponent(DB_COMPONENT)],
    ) -> CreateServerInteractor:
        return CreateServerInteractor(
            identity_provider, transaction_manager, project_repo,
        )

    @provide
    async def provide_delete_project_interactor(
        self,
        transaction_manager: Annotated[
            TransactionManagerInterface, FromComponent(DB_COMPONENT),
        ],
        identity_provider: Annotated[
            IdentityProviderInterface, FromComponent(IDENTITY_COMPONENT),
        ],
        project_repo: Annotated[ProjectRepository, FromComponent(DB_COMPONENT)],
    ) -> DeleteProjectInteractor:
        return DeleteProjectInteractor(
            identity_provider, transaction_manager, project_repo,
        )

    @provide
    async def provide_delete_server_interactor(
        self,
        transaction_manager: Annotated[
            TransactionManagerInterface, FromComponent(DB_COMPONENT),
        ],
        identity_provider: Annotated[
            IdentityProviderInterface, FromComponent(IDENTITY_COMPONENT),
        ],
        project_repo: Annotated[ProjectRepository, FromComponent(DB_COMPONENT)],
    ) -> DeleteServerInteractor:
        return DeleteServerInteractor(
            identity_provider, transaction_manager, project_repo,
        )

    @provide
    async def provide_get_project_info_interactor(
        self,
        identity_provider: Annotated[
            IdentityProviderInterface, FromComponent(IDENTITY_COMPONENT),
        ],
        project_repo: Annotated[ProjectRepository, FromComponent(DB_COMPONENT)],
    ) -> GetProjectInfoInteractor:
        return GetProjectInfoInteractor(identity_provider, project_repo)

    @provide
    async def provide_get_project_list_interactor(
        self,
        identity_provider: Annotated[
            IdentityProviderInterface, FromComponent(IDENTITY_COMPONENT),
        ],
        project_repo: Annotated[ProjectRepository, FromComponent(DB_COMPONENT)],
    ) -> GetProjectListInteractor:
        return GetProjectListInteractor(identity_provider, project_repo)

    @provide
    async def provide_show_project_config_interactor(
        self,
        transaction_manager: Annotated[
            TransactionManagerInterface, FromComponent(DB_COMPONENT),
        ],
        identity_provider: Annotated[
            IdentityProviderInterface, FromComponent(IDENTITY_COMPONENT),
        ],
        project_repo: Annotated[ProjectRepository, FromComponent(DB_COMPONENT)],
    ) -> ShowProjectConfigInteractor:
        return ShowProjectConfigInteractor(
            identity_provider, transaction_manager, project_repo,
        )

    @provide
    async def provide_update_project_config_interactor(
        self,
        transaction_manager: Annotated[
            TransactionManagerInterface, FromComponent(DB_COMPONENT),
        ],
        identity_provider: Annotated[
            IdentityProviderInterface, FromComponent(IDENTITY_COMPONENT),
        ],
        project_repo: Annotated[ProjectRepository, FromComponent(DB_COMPONENT)],
    ) -> UpdateProjectConfigInteractor:
        return UpdateProjectConfigInteractor(
            identity_provider, transaction_manager, project_repo,
        )

    @provide
    async def provide_rollback_project_config_interactor(
        self,
        transaction_manager: Annotated[
            TransactionManagerInterface, FromComponent(DB_COMPONENT),
        ],
        identity_provider: Annotated[
            IdentityProviderInterface, FromComponent(IDENTITY_COMPONENT),
        ],
        project_repo: Annotated[ProjectRepository, FromComponent(DB_COMPONENT)],
    ) -> RollbackProjectConfigInteractor:
        return RollbackProjectConfigInteractor(
            identity_provider, transaction_manager, project_repo,
        )

    @provide
    async def provide_deploy_project_interactor(
        self,
        transaction_manager: Annotated[
            TransactionManagerInterface, FromComponent(DB_COMPONENT),
        ],
        identity_provider: Annotated[
            IdentityProviderInterface, FromComponent(IDENTITY_COMPONENT),
        ],
        project_repo: Annotated[ProjectRepository, FromComponent(DB_COMPONENT)],
        deployment_repo: Annotated[
            DeploymentRepository, FromComponent(DB_COMPONENT),
        ],
    ) -> DeployProjectInteractor:
        return DeployProjectInteractor(
            transaction_manager, identity_provider, project_repo, deployment_repo,
        )

    @provide
    async def provide_get_deploy_history_interactor(
        self,
        identity_provider: Annotated[
            IdentityProviderInterface, FromComponent(IDENTITY_COMPONENT),
        ],
        project_repo: Annotated[ProjectRepository, FromComponent(DB_COMPONENT)],
        deployment_repo: Annotated[
            DeploymentRepository, FromComponent(DB_COMPONENT),
        ],
    ) -> GetDeployHistoryInteractor:
        return GetDeployHistoryInteractor(
            identity_provider, project_repo, deployment_repo,
        )

    @provide
    async def provide_get_deployment_interactor(
        self,
        identity_provider: Annotated[
            IdentityProviderInterface, FromComponent(IDENTITY_COMPONENT),
        ],
        project_repo: Annotated[ProjectRepository, FromComponent(DB_COMPONENT)],
        deployment_repo: Annotated[
            DeploymentRepository, FromComponent(DB_COMPONENT),
        ],
    ) -> GetDeploymentInteractor:
        return GetDeploymentInteractor(
            identity_provider, project_repo, deployment_repo,
        )
