from aiogram import Router
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

from deployer.presentators.tg.handlers.deployment import (
    deployments_getter,
    on_deployment_select,
    on_dialog_start,
    on_show_logs,
    on_start_deploy,
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
            'Статус: {deployment.status}\n'
            'Начало: {started_at}\n'
            'Завершение: {finished_at}\n\n'
            'Логи:\n{logs}',
        ),
        Back(Const('🔙 Назад')),
        getter=on_show_logs,
        state=DeploymentStates.deployment_logs,
    ),
    on_start=on_dialog_start,
)

router = Router()

router.include_router(deployment_dialog)
