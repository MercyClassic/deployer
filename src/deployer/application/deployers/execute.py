import asyncio
import logging
import multiprocessing
import os
import sys

from aiogram import Bot

from deployer.application.deployers.base import DeployerStrategy, SSHClient
from deployer.database.repositories.deployment import DeploymentRepository
from deployer.database.repositories.project import ProjectRepository
from deployer.database.transaction import TransactionManagerInterface
from deployer.domain.entities.deployment import DeploymentStatus
from deployer.domain.entities.project import Server
from deployer.domain.entities.project_configs import ProjectConfigType

logger = logging.getLogger(__name__)


async def _send_notification(
    deployment_id: int,
    telegram_id: int,
    status: DeploymentStatus,
) -> None:
    status_text = {
        DeploymentStatus.success: '✅ Успешно',
        DeploymentStatus.failed: '❌ Ошибка',
    }.get(status, f'⏳ {status.value}')

    text = f'Деплой #{deployment_id} завершён\nСтатус: {status_text}'

    bot = Bot(token=os.environ['BOT_TOKEN'])
    try:
        await bot.send_message(chat_id=telegram_id, text=text)
    except Exception as e:
        logger.error('Failed to send deploy notification: %s', e)
    finally:
        await bot.close()


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
                TransactionManagerInterface, 'db'
            )
            deployment_repo = await request_container.get(DeploymentRepository, 'db')
            project_repo = await request_container.get(ProjectRepository, 'db')

            deployer = deployer_cls(
                ssh_client_cls=SSHClient,
                transaction_manager=transaction_manager,
                deployment_repo=deployment_repo,
            )
            await deployer.deploy(deployment_id, config, servers)

            deployment = await deployment_repo.get(deployment_id)
            project = await project_repo.get_with_all_data(deployment.project_id)
            telegram_id = project.user.telegram_id
            status = deployment.status

        await _send_notification(deployment_id, telegram_id, status)

        sys.exit()

    process = multiprocessing.Process(
        target=lambda: asyncio.run(_execute_deploy()),
        daemon=True,
    )
    process.start()
