from aiogram import Router, types
from aiogram.filters import Command
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Cancel,
    Row,
    ScrollingGroup,
    Select,
)
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from deployer.application.interactors.deployment.deploy_project import (
    DeployProjectInteractor,
)
from deployer.presentators.tg.handlers.deployment import (
    deployments_getter,
    on_deployment_select,
    on_dialog_start,
    on_refresh_logs,
    on_show_logs,
    on_start_deploy,
    on_start_deploy_from_command,
)
from deployer.presentators.tg.states.deployment import DeploymentStates

deployment_dialog = Dialog(
    Window(
        Format('🚀 Деплои проекта\n\n{deployments_list}'),
        ScrollingGroup(
            Select(
                Format('Деплой #{item.id} ({item.status})'),
                id='deployment_select',
                item_id_getter=lambda x: x.id,
                items='deployments',
                on_click=on_deployment_select,
            ),
            id='deployments_scroll',
            width=1,
            height=5,
        ),
        Row(
            Button(
                Const('▶️ Запустить деплой'),
                id='start_deploy',
                on_click=on_start_deploy,
            ),
            Cancel(Const('🔙 Назад')),
        ),
        getter=deployments_getter,
        state=DeploymentStates.deployment_list,
    ),
    Window(
        Format(
            'Логи деплоя #{deployment.id}\n'
            'Статус: {status_emoji} {deployment.status}\n'
            'Начало: {started_at}\n'
            'Завершение: {finished_at}\n\n'
            'Логи:\n<pre>{logs}</pre>',
        ),
        Row(
            Button(
                Const('🔄 Обновить'),
                id='refresh_logs',
                on_click=on_refresh_logs,
                when='is_running',
            ),
            Back(Const('🔙 Назад')),
        ),
        getter=on_show_logs,
        state=DeploymentStates.deployment_logs,
        parse_mode='HTML',
    ),
    on_start=on_dialog_start,
)

router = Router()


@router.message(Command('deploy'))
@inject
async def deploy_handler(
    message: types.Message,
    deploy_project_interactor: FromDishka[DeployProjectInteractor],
) -> None:
    await on_start_deploy_from_command(message, deploy_project_interactor)


router.include_router(deployment_dialog)
