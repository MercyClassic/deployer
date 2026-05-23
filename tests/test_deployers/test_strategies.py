import socket
from unittest.mock import MagicMock

import pytest
from paramiko import SSHException

from deployer.application.deployers.docker import DockerDeployer
from deployer.application.deployers.git import GitDeployer
from deployer.application.deployers.shell import ShellDeployer
from deployer.domain.entities.deployment import DeploymentStatus
from deployer.domain.entities.project_configs import (
    DockerConfig,
    GitConfig,
    ShellConfig,
)
from tests.conftest import (
    InMemoryDeploymentRepo,
    InMemoryTransactionManager,
    make_deployment,
    make_server,
)


def make_fake_ssh_channel(exit_code: int = 0):
    channel = MagicMock()
    channel.recv_exit_status.return_value = exit_code
    return channel


def make_fake_stdout(output: bytes = b'ok', exit_code: int = 0):
    stdout = MagicMock()
    stdout.channel = make_fake_ssh_channel(exit_code)
    stdout.read.return_value = output
    return stdout


def make_fake_stderr(output: bytes = b''):
    stderr = MagicMock()
    stderr.read.return_value = output
    return stderr


class FakeSSHClientOk:
    def __init__(self, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def exec_command(self, command, timeout=300):
        return None, make_fake_stdout(), make_fake_stderr()


class FakeSSHClientFail:
    def __init__(self, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def exec_command(self, command, timeout=300):
        return None, make_fake_stdout(exit_code=1), make_fake_stderr(b'error output')


class FakeSSHClientConnectFail:
    def __init__(self, **kwargs):
        pass

    def __enter__(self):
        raise SSHException('Connection refused')

    def __exit__(self, *args):
        pass


class FakeSSHClientTimeout:
    def __init__(self, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def exec_command(self, command, timeout=300):
        raise socket.timeout('timed out')


def make_deployer(ssh_cls, repo=None, tx=None) -> ShellDeployer:
    repo = repo or InMemoryDeploymentRepo()
    tx = tx or InMemoryTransactionManager()
    return ShellDeployer(
        ssh_client_cls=ssh_cls,
        transaction_manager=tx,
        deployment_repo=repo,
    )


async def setup_deployment(repo: InMemoryDeploymentRepo, project_id: int = 1):
    deployment = make_deployment(project_id=project_id)
    await repo.add(deployment)
    return deployment


class TestShellDeployerSuccess:
    @pytest.mark.asyncio
    async def test_status_set_to_success(self):
        repo = InMemoryDeploymentRepo()
        deployment = await setup_deployment(repo)
        deployer = make_deployer(FakeSSHClientOk, repo)

        config = ShellConfig(commands=['echo hello', 'echo world'])
        await deployer.deploy(deployment.id, config, [make_server()])

        assert deployment.status == DeploymentStatus.success

    @pytest.mark.asyncio
    async def test_logs_contain_commands(self):
        repo = InMemoryDeploymentRepo()
        deployment = await setup_deployment(repo)
        deployer = make_deployer(FakeSSHClientOk, repo)

        config = ShellConfig(commands=['echo hello'])
        await deployer.deploy(deployment.id, config, [make_server()])

        assert 'echo hello' in deployment.std

    @pytest.mark.asyncio
    async def test_finished_at_is_set(self):
        repo = InMemoryDeploymentRepo()
        deployment = await setup_deployment(repo)
        deployer = make_deployer(FakeSSHClientOk, repo)

        config = ShellConfig(commands=['echo hello'])
        await deployer.deploy(deployment.id, config, [make_server()])

        assert deployment.finished_at is not None

    @pytest.mark.asyncio
    async def test_all_commands_appear_in_logs(self):
        repo = InMemoryDeploymentRepo()
        deployment = await setup_deployment(repo)
        deployer = make_deployer(FakeSSHClientOk, repo)

        commands = ['echo 1', 'echo 2', 'echo 3']
        config = ShellConfig(commands=commands)
        await deployer.deploy(deployment.id, config, [make_server()])

        for cmd in commands:
            assert cmd in deployment.std


class TestShellDeployerNetworkErrors:
    @pytest.mark.asyncio
    async def test_ssh_connect_failure_sets_failed_status(self):
        repo = InMemoryDeploymentRepo()
        deployment = await setup_deployment(repo)
        deployer = make_deployer(FakeSSHClientConnectFail, repo)

        config = ShellConfig(commands=['echo hello'])
        await deployer.deploy(deployment.id, config, [make_server()])

        assert deployment.status == DeploymentStatus.failed

    @pytest.mark.asyncio
    async def test_ssh_connect_failure_logs_error(self):
        repo = InMemoryDeploymentRepo()
        deployment = await setup_deployment(repo)
        deployer = make_deployer(FakeSSHClientConnectFail, repo)

        config = ShellConfig(commands=['echo hello'])
        await deployer.deploy(deployment.id, config, [make_server()])

        assert deployment.std is not None
        assert len(deployment.std) > 0

    @pytest.mark.asyncio
    async def test_timeout_sets_failed_status(self):
        repo = InMemoryDeploymentRepo()
        deployment = await setup_deployment(repo)
        deployer = make_deployer(FakeSSHClientTimeout, repo)

        config = ShellConfig(commands=['sleep 999'])
        await deployer.deploy(deployment.id, config, [make_server()])

        assert deployment.status == DeploymentStatus.failed

    @pytest.mark.asyncio
    async def test_nonzero_exit_code_sets_failed_status(self):
        repo = InMemoryDeploymentRepo()
        deployment = await setup_deployment(repo)
        deployer = make_deployer(FakeSSHClientFail, repo)

        config = ShellConfig(commands=['exit 1'])
        await deployer.deploy(deployment.id, config, [make_server()])

        assert deployment.status == DeploymentStatus.failed

    @pytest.mark.asyncio
    async def test_finished_at_set_even_on_failure(self):
        repo = InMemoryDeploymentRepo()
        deployment = await setup_deployment(repo)
        deployer = make_deployer(FakeSSHClientConnectFail, repo)

        config = ShellConfig(commands=['echo hello'])
        await deployer.deploy(deployment.id, config, [make_server()])

        assert deployment.finished_at is not None


class TestShellDeployerMultipleServers:
    @pytest.mark.asyncio
    async def test_deploys_to_all_servers(self):
        repo = InMemoryDeploymentRepo()
        deployment = await setup_deployment(repo)

        call_count = 0

        class CountingSSH:
            def __init__(self, **kwargs):
                pass

            def __enter__(self):
                nonlocal call_count
                call_count += 1
                return self

            def __exit__(self, *args):
                pass

            def exec_command(self, command, timeout=300):
                return None, make_fake_stdout(), make_fake_stderr()

        deployer = make_deployer(CountingSSH, repo)
        s1, s2, s3 = make_server(), make_server(), make_server()
        config = ShellConfig(commands=['echo hello'])
        await deployer.deploy(deployment.id, config, [s1, s2, s3])

        assert call_count == 3
        assert deployment.status == DeploymentStatus.success

    @pytest.mark.asyncio
    async def test_first_server_fail_stops_deploy(self):
        repo = InMemoryDeploymentRepo()
        deployment = await setup_deployment(repo)
        deployer = make_deployer(FakeSSHClientConnectFail, repo)

        config = ShellConfig(commands=['echo hello'])
        servers = [make_server(), make_server()]
        await deployer.deploy(deployment.id, config, servers)

        assert deployment.status == DeploymentStatus.failed


class TestGitDeployer:
    def make_git_deployer(self, ssh_cls):
        repo = InMemoryDeploymentRepo()
        tx = InMemoryTransactionManager()
        return (
            GitDeployer(
                ssh_client_cls=ssh_cls,
                transaction_manager=tx,
                deployment_repo=repo,
            ),
            repo,
        )

    @pytest.mark.asyncio
    async def test_success(self):
        deployer, repo = self.make_git_deployer(FakeSSHClientOk)
        deployment = await setup_deployment(repo)
        config = GitConfig(
            repository_url='https://github.com/user/repo',
            branch='main',
            with_entrypoint=False,
        )
        await deployer.deploy(deployment.id, config, [make_server()])
        assert deployment.status == DeploymentStatus.success

    @pytest.mark.asyncio
    async def test_ssh_failure(self):
        deployer, repo = self.make_git_deployer(FakeSSHClientConnectFail)
        deployment = await setup_deployment(repo)
        config = GitConfig(repository_url='https://github.com/user/repo')
        await deployer.deploy(deployment.id, config, [make_server()])
        assert deployment.status == DeploymentStatus.failed

    @pytest.mark.asyncio
    async def test_logs_contain_repository_url(self):
        deployer, repo = self.make_git_deployer(FakeSSHClientOk)
        deployment = await setup_deployment(repo)
        config = GitConfig(
            repository_url='https://github.com/user/repo',
            with_entrypoint=False,
        )
        await deployer.deploy(deployment.id, config, [make_server()])
        assert 'https://github.com/user/repo' in deployment.std


class TestDockerDeployer:
    def make_docker_deployer(self, ssh_cls):
        repo = InMemoryDeploymentRepo()
        tx = InMemoryTransactionManager()
        return (
            DockerDeployer(
                ssh_client_cls=ssh_cls,
                transaction_manager=tx,
                deployment_repo=repo,
            ),
            repo,
        )

    @pytest.mark.asyncio
    async def test_success(self):
        deployer, repo = self.make_docker_deployer(FakeSSHClientOk)
        deployment = await setup_deployment(repo)
        config = DockerConfig(
            image='myapp:latest',
            registry_url='registry.example.com',
            volumes=None,
            ports=None,
            network=None,
            env=None,
        )
        await deployer.deploy(deployment.id, config, [make_server()])
        assert deployment.status == DeploymentStatus.success

    @pytest.mark.asyncio
    async def test_ssh_failure(self):
        deployer, repo = self.make_docker_deployer(FakeSSHClientConnectFail)
        deployment = await setup_deployment(repo)
        config = DockerConfig(
            image='myapp:latest',
            registry_url='registry.example.com',
            volumes=None,
            ports=None,
            network=None,
            env=None,
        )
        await deployer.deploy(deployment.id, config, [make_server()])
        assert deployment.status == DeploymentStatus.failed

    @pytest.mark.asyncio
    async def test_logs_contain_docker_pull(self):
        deployer, repo = self.make_docker_deployer(FakeSSHClientOk)
        deployment = await setup_deployment(repo)
        config = DockerConfig(
            image='myapp:latest',
            registry_url='registry.example.com',
            volumes=None,
            ports=None,
            network=None,
            env=None,
        )
        await deployer.deploy(deployment.id, config, [make_server()])
        assert 'docker pull' in deployment.std

    @pytest.mark.asyncio
    async def test_logs_contain_docker_run(self):
        deployer, repo = self.make_docker_deployer(FakeSSHClientOk)
        deployment = await setup_deployment(repo)
        config = DockerConfig(
            image='myapp:latest',
            registry_url='registry.example.com',
            volumes=None,
            ports=None,
            network=None,
            env=None,
        )
        await deployer.deploy(deployment.id, config, [make_server()])
        assert 'docker run' in deployment.std


class TestLiveLogs:
    @pytest.mark.asyncio
    async def test_std_updated_during_deploy(self):
        flush_snapshots = []

        class TrackingRepo(InMemoryDeploymentRepo):
            async def update_std(self, deployment_id, std):
                flush_snapshots.append(std)
                await super().update_std(deployment_id, std)

        repo = TrackingRepo()
        deployment = await setup_deployment(repo)
        deployer = ShellDeployer(
            ssh_client_cls=FakeSSHClientOk,
            transaction_manager=InMemoryTransactionManager(),
            deployment_repo=repo,
        )

        config = ShellConfig(commands=['echo 1', 'echo 2'])
        await deployer.deploy(deployment.id, config, [make_server()])

        assert len(flush_snapshots) > 0
        assert len(flush_snapshots[-1]) >= len(flush_snapshots[0])
