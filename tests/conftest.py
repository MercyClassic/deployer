import datetime
import pytest

from deployer.domain.entities.deployment import Deployment, DeploymentStatus
from deployer.domain.entities.project import DeployStrategy, Project, ProjectConfig, Server
from deployer.domain.entities.project_configs import ShellConfig, GitConfig, DockerConfig


# ---------------------------------------------------------------------------
# In-memory repositories
# ---------------------------------------------------------------------------

class InMemoryDeploymentRepo:
    def __init__(self):
        self._store: dict[int, Deployment] = {}
        self._next_id = 1

    async def add(self, deployment: Deployment) -> None:
        deployment.id = self._next_id
        self._next_id += 1
        self._store[deployment.id] = deployment

    async def get(self, deployment_id: int) -> Deployment | None:
        return self._store.get(deployment_id)

    async def get_history(self, project_id: int):
        return [d for d in self._store.values() if d.project_id == project_id]

    async def update_std(self, deployment_id: int, std: str) -> None:
        if deployment_id in self._store:
            self._store[deployment_id].std = std


class InMemoryTransactionManager:
    async def commit(self) -> None:
        pass

    async def flush(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_project(user_id: int = 1, strategy: DeployStrategy = DeployStrategy.shell) -> Project:
    project = Project(
        user_id=user_id,
        name='test-project',
        deploy_strategy=strategy,
        created_at=datetime.datetime.now(datetime.UTC),
    )
    project.id = 1
    project.configs = []
    project.servers = []
    project.deployments = []
    project.user = None
    return project


def make_server(project_id: int = 1) -> Server:
    server = Server(
        project_id=project_id,
        name='test-server',
        host='1.2.3.4',
        port=22,
        ssh_user='deploy',
        ssh_secret='secret',
        workdir='/app',
        created_at=None,
    )
    server.id = 1
    server.project = None
    return server


def make_shell_config(project_id: int = 1, version: int = 1, active: bool = True) -> ProjectConfig:
    config = ProjectConfig(
        project_id=project_id,
        version=version,
        config=ShellConfig(commands=['echo hello']),
        strategy=DeployStrategy.shell,
        created_at=None,
        is_active=active,
    )
    config.id = version
    config.project = None
    return config


def make_deployment(project_id: int = 1, status: DeploymentStatus = DeploymentStatus.pending) -> Deployment:
    deployment = Deployment.create(project_id=project_id, status=status)
    deployment.id = 1
    deployment.project = None
    return deployment


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def deployment_repo():
    return InMemoryDeploymentRepo()


@pytest.fixture
def transaction_manager():
    return InMemoryTransactionManager()


@pytest.fixture
def project():
    return make_project()


@pytest.fixture
def server():
    return make_server()