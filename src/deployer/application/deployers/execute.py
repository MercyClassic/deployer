import asyncio
import multiprocessing
import sys

from deployer.application.deployers.base import DeployerStrategy, SSHClient
from deployer.database.repositories.deployment import DeploymentRepository
from deployer.database.transaction import TransactionManagerInterface
from deployer.domain.entities.project import Server
from deployer.domain.entities.project_configs import ProjectConfigType


def execute_deploy(
    deployer_cls: type[DeployerStrategy],
    deployment_id: int,
    config: ProjectConfigType,
    servers: list[Server],
) -> None:
    async def _execute_deploy() -> None:
        from deployer.main.providers.build import build_container

        container = build_container()
        async with container() as request_container:
            transaction_manager = await request_container.get(
                TransactionManagerInterface, 'db',
            )
            deployment_repo = await request_container.get(DeploymentRepository, 'db')

            deployer = deployer_cls(
                ssh_client_cls=SSHClient,
                transaction_manager=transaction_manager,
                deployment_repo=deployment_repo,
            )
            await deployer.deploy(deployment_id, config, servers)

        sys.exit()

    process = multiprocessing.Process(
        target=lambda: asyncio.run(_execute_deploy()),
        daemon=True,
    )
    process.start()
