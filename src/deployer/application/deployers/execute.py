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
    }.get(status, f'⏳ {status}')

    text = f'Деплой #{deployment_id} завершён\nСтатус: {status_text}'

    bot = Bot(token=os.environ['BOT_TOKEN'])
    try:
        await bot.send_message(chat_id=telegram_id, text=text)
    except Exception as e:
        logger.error('Failed to send deploy notification: %s', e)
    finally:
        await bot.session.close()


async def _run_deploy(
    deployer_cls: type[DeployerStrategy],
    deployment_id: int,
    config: ProjectConfigType,
) -> None:
    from deployer.database.mapper import start_db_mapping
    from deployer.main.providers.build import build_container

    start_db_mapping()
    container = build_container()
    async with container() as request_container:
        transaction_manager = await request_container.get(
            TransactionManagerInterface, 'db'
        )
        deployment_repo = await request_container.get(DeploymentRepository, 'db')
        project_repo = await request_container.get(ProjectRepository, 'db')

        deployment = await deployment_repo.get(deployment_id)
        project = await project_repo.get_with_all_data(deployment.project_id)

        deployer = deployer_cls(
            ssh_client_cls=SSHClient,
            transaction_manager=transaction_manager,
            deployment_repo=deployment_repo,
        )
        await deployer.deploy(deployment_id, config, project.servers)

        await deployment_repo.refresh(deployment)

    await _send_notification(
        deployment_id, project.user.telegram_id, deployment.status
    )


def _process_entrypoint(
    deployer_cls: type[DeployerStrategy],
    deployment_id: int,
    config: ProjectConfigType,
) -> None:
    asyncio.run(_run_deploy(deployer_cls, deployment_id, config))
    sys.exit()


def execute_deploy(
    deployer_cls: type[DeployerStrategy],
    deployment_id: int,
    config: ProjectConfigType,
) -> None:
    process = multiprocessing.Process(
        target=_process_entrypoint,
        args=(deployer_cls, deployment_id, config),
        daemon=True,
    )
    process.start()
