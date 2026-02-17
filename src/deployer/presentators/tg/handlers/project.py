import json
import re

import yaml
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

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
from deployer.domain.exceptions.project import (
    ActiveConfigNotFound,
    ImpossibleProjectConfigVersion,
    InvalidConfigFormat,
    InvalidDeployStrategy,
)
from deployer.presentators.tg.states.deployment import DeploymentStates
from deployer.presentators.tg.states.project import ProjectStates


@inject
async def projects_getter(
    get_project_list_interactor: FromDishka[GetProjectListInteractor],
    **kwargs,
) -> dict:
    projects = await get_project_list_interactor.execute()
    return {'projects': projects}


@inject
async def on_project_select(
    callback: CallbackQuery,
    widget,
    manager: DialogManager,
    item_id: str,
) -> None:
    manager.dialog_data['project_id'] = int(item_id)
    await manager.switch_to(ProjectStates.project_menu)


@inject
async def project_info_getter(
    dialog_manager: DialogManager,
    get_project_info_interactor: FromDishka[GetProjectInfoInteractor],
    **kwargs,
) -> dict:
    project_id = dialog_manager.dialog_data['project_id']
    project = await get_project_info_interactor.execute(project_id)
    created_at = (
        project.created_at.strftime('%d.%m.%Y %H:%M')
        if project.created_at
        else 'N/A'
    )

    return {'project': project, 'created_at': created_at}


async def on_project_name_entered(
    message: Message,
    widget: ManagedTextInput,
    manager: DialogManager,
    text: str,
) -> None:
    manager.dialog_data['project_name'] = text
    await manager.switch_to(ProjectStates.project_strategy)


async def on_project_strategy_entered(
    message: Message,
    widget: ManagedTextInput,
    manager: DialogManager,
    text: str,
) -> None:
    manager.dialog_data['project_strategy'] = text
    await manager.switch_to(ProjectStates.project_confirm)


@inject
async def on_confirm_create_project(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    create_project_interactor: FromDishka[CreateProjectInteractor],
) -> None:
    project_name = manager.dialog_data['project_name']
    project_strategy = manager.dialog_data['project_strategy']

    try:
        project = await create_project_interactor.execute(
            name=project_name,
            deploy_strategy=project_strategy,
        )
    except InvalidDeployStrategy:
        await callback.answer(
            'Произошла ошибка при создании проекта. '
            'Вероятнее всего мы указали неверную стратегию деплоя. '
            'Повторите попытку ещё раз.',
        )
        await manager.switch_to(ProjectStates.project_create)
        return

    manager.dialog_data['project_id'] = project.id
    await callback.answer(f'Проект "{project.name}" создан')
    await manager.switch_to(ProjectStates.project_menu)


@inject
async def on_delete_project(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    delete_project_interactor: FromDishka[DeleteProjectInteractor],
) -> None:
    project_id = manager.dialog_data['project_id']
    await delete_project_interactor.execute(project_id)
    await callback.answer('Проект удален')
    await manager.switch_to(ProjectStates.project_list)


@inject
async def config_getter(
    dialog_manager: DialogManager,
    show_project_config_interactor: FromDishka[ShowProjectConfigInteractor],
    **kwargs,
) -> dict:
    project_id = dialog_manager.dialog_data['project_id']

    try:
        config = await show_project_config_interactor.execute(project_id)
    except ActiveConfigNotFound:
        return {
            'config': None,
            'version': 'нет',
            'content': 'Конфиг не найден',
            'has_config': False,
        }

    config_json = json.dumps(config.config.to_dict(), indent=2, ensure_ascii=False)
    return {
        'config': config,
        'version': config.version,
        'content': f'<code>{config_json}</code>',
        'has_config': True,
    }


@inject
async def config_versions_getter(
    dialog_manager: DialogManager,
    get_project_info_interactor: FromDishka[GetProjectInfoInteractor],
    **kwargs,
) -> dict:
    project_id = dialog_manager.dialog_data['project_id']

    project = await get_project_info_interactor.execute(project_id)
    configs = (
        list(
            filter(lambda x: x.strategy == project.deploy_strategy, project.configs),
        )
        if hasattr(project, 'configs')
        else []
    )

    return {
        'configs': sorted(configs, key=lambda x: x.version, reverse=True),
        'has_configs': len(configs) > 0,
        'no_configs': len(configs) == 0,
    }


@inject
async def on_config_version_select(
    callback: CallbackQuery,
    widget,
    manager: DialogManager,
    item_id: str,
    rollback_project_config_interactor: FromDishka[RollbackProjectConfigInteractor],
) -> None:
    project_id = manager.dialog_data['project_id']
    config_version = int(item_id)

    try:
        config = await rollback_project_config_interactor.execute(
            project_id,
            config_version,
        )
    except ImpossibleProjectConfigVersion:
        await callback.answer(
            'Выбрана несуществующая или текущая версия конфига для отката',
        )
        return

    await callback.answer(f'Конфиг откачен до версии v{config.version}')
    await manager.switch_to(ProjectStates.config_show)


def parse_config_content(text: str) -> dict:
    pattern = r'```(?:json|yaml|yml)?\n?(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    content = matches[0].strip() if matches else text.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    try:
        return yaml.safe_load(content)
    except yaml.YAMLError:
        pass

    raise ValueError('Не удалось распарсить как JSON или YAML')


@inject
async def on_config_text_received(
    message: Message,
    widget,
    manager: DialogManager,
    update_project_config_interactor: FromDishka[UpdateProjectConfigInteractor],
) -> None:
    project_id = manager.dialog_data.get('project_id')
    if not project_id:
        await message.answer('Ошибка: проект не выбран')
        return

    config = parse_config_content(message.text)

    try:
        updated_config = await update_project_config_interactor.execute(
            project_id,
            config,
        )
    except InvalidConfigFormat:
        await message.answer(
            '❌ Неправильный формат конфига. Убедитесь в его корректности',
        )
        return

    await message.answer(f'✅ Конфиг обновлен. Версия v{updated_config.version}')
    await manager.switch_to(ProjectStates.config_show)


@inject
async def servers_getter(
    dialog_manager: DialogManager,
    get_project_info_interactor: FromDishka[GetProjectInfoInteractor],
    **kwargs,
) -> dict:
    project_id = dialog_manager.dialog_data['project_id']
    project = await get_project_info_interactor.execute(project_id)
    servers = (
        project.servers if hasattr(project, 'servers') and project.servers else []
    )

    if not servers:
        return {
            'servers': [],
            'servers_list': 'Серверы отсутствуют',
            'has_servers': False,
        }

    return {
        'servers': project.servers,
        'servers_list': '\n'.join(
            [
                f'{i + 1}. {server.name} '
                f'({server.host}:{server.port}) - {server.ssh_user}@{server.workdir}'
                for i, server in enumerate(project.servers)
            ],
        ),
        'has_servers': True,
    }


async def on_server_select(
    callback: CallbackQuery,
    widget,
    manager: DialogManager,
    item_id: str,
) -> None:
    manager.dialog_data['server_id'] = int(item_id)
    await manager.switch_to(ProjectStates.server_info)


@inject
async def server_info_getter(
    dialog_manager: DialogManager,
    get_project_info_interactor: FromDishka[GetProjectInfoInteractor],
    **kwargs,
) -> dict:
    project_id = dialog_manager.dialog_data['project_id']
    server_id = dialog_manager.dialog_data.get('server_id')

    if not server_id or not project_id:
        return {'server': None}

    project = await get_project_info_interactor.execute(project_id)
    server = next((s for s in project.servers if s.id == server_id), None)

    return {'server': server}


@inject
async def on_delete_server(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    delete_server_interactor: FromDishka[DeleteServerInteractor],
) -> None:
    project_id = manager.dialog_data['project_id']
    server_id = manager.dialog_data['server_id']

    await delete_server_interactor.execute(project_id, server_id)
    await callback.answer('Сервер удален')
    await manager.switch_to(ProjectStates.servers_list)


async def on_server_name_entered(
    message: Message,
    widget: ManagedTextInput,
    manager: DialogManager,
    text: str,
) -> None:
    manager.dialog_data['server_name'] = text
    await manager.switch_to(ProjectStates.server_host)


async def on_server_host_entered(
    message: Message,
    widget: ManagedTextInput,
    manager: DialogManager,
    text: str,
) -> None:
    manager.dialog_data['server_host'] = text
    await manager.switch_to(ProjectStates.server_user)


async def on_server_user_entered(
    message: Message,
    widget: ManagedTextInput,
    manager: DialogManager,
    text: str,
) -> None:
    manager.dialog_data['server_user'] = text
    await manager.switch_to(ProjectStates.server_secret)


async def on_server_secret_entered(
    message: Message,
    widget: ManagedTextInput,
    manager: DialogManager,
    text: str,
) -> None:
    manager.dialog_data['server_secret'] = text
    await manager.switch_to(ProjectStates.server_workdir)


async def on_server_workdir_entered(
    message: Message,
    widget: ManagedTextInput,
    manager: DialogManager,
    text: str,
) -> None:
    manager.dialog_data['server_workdir'] = text
    await manager.switch_to(ProjectStates.server_port)


async def on_server_port_entered(
    message: Message,
    widget: ManagedTextInput,
    manager: DialogManager,
    text: str,
) -> None:
    try:
        port = int(text)
        manager.dialog_data['server_port'] = port
    except ValueError:
        manager.dialog_data['server_port'] = 22

    await manager.switch_to(ProjectStates.server_confirm)


@inject
async def on_confirm_add_server(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    create_server_interactor: FromDishka[CreateServerInteractor],
) -> None:
    server = await create_server_interactor.execute(
        project_id=manager.dialog_data['project_id'],
        name=manager.dialog_data['server_name'],
        host=manager.dialog_data['server_host'],
        ssh_user=manager.dialog_data['server_user'],
        ssh_secret=manager.dialog_data['server_secret'],
        workdir=manager.dialog_data['server_workdir'],
        port=manager.dialog_data['server_port'],
    )

    await callback.answer(f'Сервер "{server.name}" добавлен')
    await manager.switch_to(ProjectStates.servers_list)


async def on_deployment_dialog_start(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        DeploymentStates.deployment_list,
        data={'project_id': dialog_manager.dialog_data['project_id']},
        show_mode=ShowMode.EDIT,
    )


async def on_new_strategy_entered(
    message: Message,
    widget: ManagedTextInput,
    manager: DialogManager,
    text: str,
) -> None:
    manager.dialog_data['new_strategy'] = text
    await manager.switch_to(ProjectStates.project_strategy_confirm)


@inject
async def on_confirm_strategy_change(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    update_project_strategy_interactor: FromDishka[UpdateProjectStrategyInteractor],
) -> None:
    project_id = manager.dialog_data['project_id']
    new_strategy = manager.dialog_data['new_strategy']

    try:
        project = await update_project_strategy_interactor.execute(
            project_id,
            new_strategy,
        )
        await callback.answer(f'✅ Стратегия изменена на {project.deploy_strategy}')
        await manager.switch_to(ProjectStates.project_menu)
    except InvalidDeployStrategy:
        await callback.answer('❌ Выбрана некорректная стратегия деплоя')
