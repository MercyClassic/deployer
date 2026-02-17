import logging
from abc import ABC, abstractmethod

import paramiko
from paramiko import SSHException

from deployer.database.repositories.deployment import DeploymentRepository
from deployer.database.transaction import TransactionManagerInterface
from deployer.domain.entities.deployment import DeploymentStatus
from deployer.domain.entities.project import Server
from deployer.domain.entities.project_configs import ProjectConfigType
from deployer.domain.exceptions.deployment import DeployFailed

logger = logging.getLogger(__name__)


class SSHClient:
    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        port: int = 22,
        timeout: float = 10.0,
    ):
        self.host = host
        self.username = user
        self.password = password
        self.port = port
        self.timeout = timeout

        self.client: paramiko.SSHClient | None = None

    def __enter__(self) -> paramiko.SSHClient:
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            hostname=self.host,
            username=self.username,
            password=self.password,
            port=self.port,
            timeout=self.timeout,
        )
        return self.client

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.client:
            self.client.close()


class DeployerStrategy(ABC):
    def __init__(
        self,
        ssh_client_cls: type[SSHClient],
        transaction_manager: TransactionManagerInterface,
        deployment_repo: DeploymentRepository,
    ):
        self._ssh_client = ssh_client_cls
        self._transaction_manager = transaction_manager
        self._deployment_repo = deployment_repo
        self.logs = []

    def _run_command(self, ssh_client, command: str) -> None:
        self.logs.append(f'$ {command}')

        stdin, stdout, stderr = ssh_client.exec_command(command)
        channel = stdout.channel

        stdin, stdout, stderr = ssh_client.exec_command(command)
        out = stdout.read().decode()
        err = stderr.read().decode()
        if out:
            self.logs.append(out)
        if err:
            self.logs.append(err)

        exit_code = channel.recv_exit_status()

        if exit_code != 0:
            raise DeployFailed(f'Command failed with exit code {exit_code}')

    @abstractmethod
    async def _deploy(
        self,
        config: ProjectConfigType,
        servers: list[Server],
    ) -> None:
        raise NotImplementedError

    async def deploy(
        self,
        deployment_id: int,
        config: ProjectConfigType,
        servers: list[Server],
    ) -> None:
        deployment = await self._deployment_repo.get(deployment_id)
        deployment.set_status(DeploymentStatus.running)
        await self._transaction_manager.commit()
        try:
            await self._deploy(config, servers)
        except (DeployFailed, SSHException) as exc:
            logger.error('Deploy #%s failed. Reason: %s', deployment.id, str(exc))
            self.logs.append(str(exc))
            deployment.set_status(DeploymentStatus.failed)
        else:
            deployment.set_status(DeploymentStatus.success)

        deployment.set_finished_at()
        deployment.set_std('\n'.join(self.logs))

        await self._transaction_manager.commit()
