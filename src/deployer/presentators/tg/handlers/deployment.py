from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from deployer.application.interactors.deployment.deploy_project import (
    DeployProjectInteractor,
)
from deployer.application.interactors.deployment.get_deploy_history import (
    GetDeployHistoryInteractor,
)
from deployer.application.interactors.deployment.get_deployment import (
    GetDeploymentInteractor,
)
from deployer.domain.exceptions.project import ActiveConfigNotFound
from deployer.presentators.tg.states.deployment import DeploymentStates


async def on_dialog_start(start_data: dict, manager: DialogManager) -> None:
    if start_data:
        manager.dialog_data.update(start_data)


@inject
async def deployments_getter(
    dialog_manager: DialogManager,
    get_deploy_history_interactor: FromDishka[GetDeployHistoryInteractor],
    **kwargs,
) -> dict:
    project_id = dialog_manager.dialog_data['project_id']

    deployments = await get_deploy_history_interactor.execute(project_id)

    if not deployments:
        return {'deployments': [], 'deployments_list': 'История деплоев пуста'}

    status_emoji_mapper = {
        'success': '✅',
        'failed': '❌',
        'default': '⏳',
    }
    deployments_list = '\n'.join(
        [
            f'{status_emoji_mapper.get(deploy.status, status_emoji_mapper['default'])} '
            f'Деплой #{deploy.id} - {deploy.status} '
            f'({deploy.started_at.strftime("%d.%m.%Y %H:%M") if deploy.started_at else "N/A"})'
            for deploy in deployments
        ],
    )

    return {'deployments': deployments, 'deployments_list': deployments_list}


async def on_deployment_select(
    callback: CallbackQuery,
    widget: Select,
    manager: DialogManager,
    item_id: str,
) -> None:
    manager.dialog_data['deployment_id'] = int(item_id)
    await manager.switch_to(DeploymentStates.deployment_logs)


@inject
async def on_start_deploy(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    deploy_project_interactor: FromDishka[DeployProjectInteractor],
) -> None:
    project_id = manager.dialog_data.get('project_id')
    if not project_id:
        await callback.answer('Ошибка: проект не выбран')
        return

    try:
        deployment = await deploy_project_interactor.execute(project_id)
    except ActiveConfigNotFound:
        await callback.answer('❌ Не найдена конфигурация проекта')
        return

    await callback.answer(f'🚀 Деплой #{deployment.id} запущен')
    await manager.switch_to(DeploymentStates.deployment_list)


@inject
async def on_show_logs(
    dialog_manager: DialogManager,
    get_deployment_interactor: FromDishka[GetDeploymentInteractor],
    **kwargs,
) -> dict:
    deployment_id = dialog_manager.dialog_data['deployment_id']

    deployment = await get_deployment_interactor.execute(deployment_id)

    started_at = (
        deployment.started_at.strftime('%d.%m.%Y %H:%M')
        if deployment.started_at
        else 'N/A'
    )
    finished_at = (
        deployment.finished_at.strftime('%d.%m.%Y %H:%M')
        if deployment.finished_at
        else 'N/A'
    )

    return {
        'deployment': deployment,
        'logs': deployment.std[:3000] if deployment.std else 'Логи отсутствуют',
        'started_at': started_at,
        'finished_at': finished_at,
    }
