from aiogram import Router
from aiogram.enums import ParseMode
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Group,
    Row,
    ScrollingGroup,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format

from deployer.presentators.tg.handlers.project import (
    config_getter,
    config_versions_getter,
    on_config_text_received,
    on_config_version_select,
    on_confirm_add_server,
    on_confirm_create_project,
    on_confirm_strategy_change,
    on_delete_project,
    on_delete_server,
    on_deployment_dialog_start,
    on_new_strategy_entered,
    on_project_name_entered,
    on_project_select,
    on_project_strategy_entered,
    on_server_host_entered,
    on_server_name_entered,
    on_server_port_entered,
    on_server_secret_entered,
    on_server_select,
    on_server_user_entered,
    on_server_workdir_entered,
    project_info_getter,
    projects_getter,
    server_info_getter,
    servers_getter,
)
from deployer.presentators.tg.states.project import ProjectStates

project_dialog = Dialog(
    Window(
        Const('📁 Ваши проекты:'),
        ScrollingGroup(
            Select(
                Format('{item.name} (ID: {item.id})'),
                id='project_select',
                item_id_getter=lambda x: x.id,
                items='projects',
                on_click=on_project_select,
            ),
            id='projects_scroll',
            width=1,
            height=5,
        ),
        Row(
            SwitchTo(
                Const('➕ Создать проект'),
                id='create_project',
                state=ProjectStates.project_create,
            ),
            Cancel(Const('🔙 Назад')),
        ),
        getter=projects_getter,
        state=ProjectStates.project_list,
    ),
    Window(
        Const('Создание проекта'),
        Const('Введите название проекта:'),
        TextInput(
            id='project_name_input',
            on_success=on_project_name_entered,
        ),
        SwitchTo(
            Const('🔙 Назад'),
            id='back_to_projects',
            state=ProjectStates.project_list,
        ),
        state=ProjectStates.project_create,
    ),
    Window(
        Const('Создание проекта'),
        Format('Название: {dialog_data[project_name]}'),
        Const('Введите стратегию деплоя - shell | git | docker:'),
        TextInput(
            id='project_strategy_input',
            on_success=on_project_strategy_entered,
        ),
        SwitchTo(
            Const('🔙 Назад'),
            id='back_to_project_name',
            state=ProjectStates.project_create,
        ),
        state=ProjectStates.project_strategy,
    ),
    Window(
        Const('Создание проекта'),
        Format(
            'Проверьте данные:\n\n'
            'Название: {dialog_data[project_name]}\n'
            'Стратегия: {dialog_data[project_strategy]}',
        ),
        Row(
            Button(
                Const('✅ Создать'),
                id='confirm_create_project',
                on_click=on_confirm_create_project,
            ),
            SwitchTo(
                Const('🔙 Назад'),
                id='back_to_project_strategy',
                state=ProjectStates.project_strategy,
            ),
        ),
        state=ProjectStates.project_confirm,
    ),
    Window(
        Format(
            'Проект: {project.name}\n'
            'ID: {project.id}\n'
            'Стратегия: {project.deploy_strategy}\n'
            'Создан: {created_at}\n\n'
            'Что делаем с проектом?',
        ),
        Group(
            SwitchTo(
                Const('📋 Конфиг'),
                id='config_menu',
                state=ProjectStates.config_show,
            ),
            SwitchTo(
                Const('🖥️ Серверы'),
                id='servers_menu',
                state=ProjectStates.servers_list,
            ),
            SwitchTo(
                Const('⚙️ Стратегия'),
                id='strategy_menu',
                state=ProjectStates.project_strategy_change,
            ),
            Button(
                Const('🚀 Деплои'),
                id='deployments_menu',
                on_click=on_deployment_dialog_start,
            ),
            width=2,
        ),
        Row(
            Button(
                Const('🗑️ Удалить проект'),
                id='delete_project',
                on_click=on_delete_project,
            ),
            SwitchTo(
                Const('🔙 Назад'),
                id='back_to_projects_list',
                state=ProjectStates.project_list,
            ),
        ),
        getter=project_info_getter,
        state=ProjectStates.project_menu,
    ),
    Window(
        Format('⚙️ Конфигурация проекта\n\nТекущая версия: {version}\n\n{content}'),
        Row(
            SwitchTo(
                Const('🔄 Обновить'),
                id='upload_config',
                state=ProjectStates.config_upload,
            ),
            SwitchTo(
                Const('⏪ Откатить'),
                id='rollback_config',
                state=ProjectStates.config_rollback,
            ),
        ),
        SwitchTo(
            Const('🔙 Назад'),
            id='back_to_project_menu',
            state=ProjectStates.project_menu,
        ),
        getter=config_getter,
        state=ProjectStates.config_show,
        parse_mode=ParseMode.HTML,
    ),
    Window(
        Const(
            'Отправьте новый конфиг в формате JSON/YAML. Например:\n'
            '```json\n{\n  "ключ": "значение"\n}\n```',
        ),
        MessageInput(func=on_config_text_received),
        SwitchTo(
            Const('🔙 Назад'),
            id='back_to_config_show',
            state=ProjectStates.config_show,
        ),
        state=ProjectStates.config_upload,
    ),
    Window(
        Const(
            'Выберите версию для отката:',
            when='has_configs',
        ),
        Const(
            'Нет версий для отката',
            when='no_configs',
        ),
        ScrollingGroup(
            Select(
                Format('v{item.version}'),
                id='config_version_select',
                item_id_getter=lambda x: x.version,
                items='configs',
                on_click=on_config_version_select,
            ),
            id='configs_scroll',
            width=1,
            height=5,
        ),
        SwitchTo(
            Const('🔙 Назад'),
            id='back_to_config_show_from_rollback',
            state=ProjectStates.config_show,
        ),
        getter=config_versions_getter,
        state=ProjectStates.config_rollback,
    ),
    Window(
        Format('🖥️ Серверы проекта\n\n{servers_list}'),
        ScrollingGroup(
            Select(
                Format('{item.name} ({item.host}:{item.port})'),
                id='server_select',
                item_id_getter=lambda x: x.id,
                items='servers',
                on_click=on_server_select,
            ),
            id='servers_scroll',
            width=1,
            height=5,
        ),
        Row(
            SwitchTo(
                Const('➕ Добавить сервер'),
                id='add_server',
                state=ProjectStates.server_add,
            ),
            SwitchTo(
                Const('🔙 Назад'),
                id='back_to_project_menu_from_servers',
                state=ProjectStates.project_menu,
            ),
        ),
        getter=servers_getter,
        state=ProjectStates.servers_list,
    ),
    Window(
        Format(
            'Информация о сервере:\n\n'
            'Имя: {server.name}\n'
            'Хост: {server.host}:{server.port}\n'
            'Пользователь: {server.ssh_user}\n'
            'Рабочая директория: {server.workdir}\n',
        ),
        Row(
            Button(
                Const('🗑️ Удалить сервер'),
                id='delete_server_button',
                on_click=on_delete_server,
            ),
            SwitchTo(
                Const('🔙 Назад'),
                id='back_to_servers_list',
                state=ProjectStates.servers_list,
            ),
        ),
        getter=server_info_getter,
        state=ProjectStates.server_info,
    ),
    Window(
        Const('Добавление сервера'),
        Const('Введите название сервера:'),
        TextInput(id='server_name_input', on_success=on_server_name_entered),
        SwitchTo(
            Const('🔙 Назад'),
            id='back_to_servers_list_from_add',
            state=ProjectStates.servers_list,
        ),
        state=ProjectStates.server_add,
    ),
    Window(
        Const('Добавление сервера'),
        Format('Название: {dialog_data[server_name]}'),
        Const('Введите хост сервера:'),
        TextInput(id='server_host_input', on_success=on_server_host_entered),
        SwitchTo(
            Const('🔙 Назад'),
            id='back_to_server_name',
            state=ProjectStates.server_add,
        ),
        state=ProjectStates.server_host,
    ),
    Window(
        Const('Добавление сервера'),
        Format(
            'Название: {dialog_data[server_name]}\n'
            'Хост: {dialog_data[server_host]}',
        ),
        Const('Введите пользователя SSH:'),
        TextInput(id='server_user_input', on_success=on_server_user_entered),
        SwitchTo(
            Const('🔙 Назад'),
            id='back_to_server_host',
            state=ProjectStates.server_host,
        ),
        state=ProjectStates.server_user,
    ),
    Window(
        Const('Добавление сервера'),
        Format(
            'Название: {dialog_data[server_name]}\n'
            'Хост: {dialog_data[server_host]}\n'
            'Пользователь: {dialog_data[server_user]}',
        ),
        Const('Введите секрет (пароль/ключ):'),
        TextInput(id='server_secret_input', on_success=on_server_secret_entered),
        SwitchTo(
            Const('🔙 Назад'),
            id='back_to_server_user',
            state=ProjectStates.server_user,
        ),
        state=ProjectStates.server_secret,
    ),
    Window(
        Const('Добавление сервера'),
        Format(
            'Название: {dialog_data[server_name]}\n'
            'Хост: {dialog_data[server_host]}\n'
            'Пользователь: {dialog_data[server_user]}\n'
            'Пароль: *****\n',
        ),
        Const('Введите рабочую директорию:'),
        TextInput(id='server_workdir_input', on_success=on_server_workdir_entered),
        SwitchTo(
            Const('🔙 Назад'),
            id='back_to_server_secret',
            state=ProjectStates.server_secret,
        ),
        state=ProjectStates.server_workdir,
    ),
    Window(
        Const('Добавление сервера'),
        Format(
            'Название: {dialog_data[server_name]}\n'
            'Хост: {dialog_data[server_host]}\n'
            'Пользователь: {dialog_data[server_user]}\n'
            'Пароль: *****\n'
            'Директория: {dialog_data[server_workdir]}',
        ),
        Const('Введите порт SSH (по умолчанию 22):'),
        TextInput(id='server_port_input', on_success=on_server_port_entered),
        SwitchTo(
            Const('🔙 Назад'),
            id='back_to_server_workdir',
            state=ProjectStates.server_workdir,
        ),
        state=ProjectStates.server_port,
    ),
    Window(
        Const('Добавление сервера'),
        Format(
            'Проверьте данные:\n\n'
            'Название: {dialog_data[server_name]}\n'
            'Хост: {dialog_data[server_host]}\n'
            'Пользователь: {dialog_data[server_user]}\n'
            'Пароль: *****\n'
            'Директория: {dialog_data[server_workdir]}\n'
            'Порт: {dialog_data[server_port]}',
        ),
        Row(
            Button(
                Const('✅ Добавить'),
                id='confirm_add_server',
                on_click=on_confirm_add_server,
            ),
            SwitchTo(
                Const('🔙 Назад'),
                id='back_to_server_port',
                state=ProjectStates.server_port,
            ),
        ),
        state=ProjectStates.server_confirm,
    ),
    Window(
        Const('Изменение стратегии деплоя'),
        Format('Текущая стратегия: {project.deploy_strategy}'),
        Const('Введите новую стратегию (shell | git | docker):'),
        TextInput(
            id='new_strategy_input',
            on_success=on_new_strategy_entered,
        ),
        SwitchTo(
            Const('🔙 Назад'),
            id='back_to_project_menu_from_strategy',
            state=ProjectStates.project_menu,
        ),
        getter=project_info_getter,
        state=ProjectStates.project_strategy_change,
    ),
    Window(
        Const('Подтверждение изменения стратегии'),
        Format(
            'Проверьте данные:\n\n'
            'Проект: {project.name}\n'
            'Текущая стратегия: {project.deploy_strategy.value}\n'
            'Новая стратегия: {dialog_data[new_strategy]}',
        ),
        Row(
            Button(
                Const('✅ Подтвердить'),
                id='confirm_strategy_change',
                on_click=on_confirm_strategy_change,
            ),
            SwitchTo(
                Const('🔙 Назад'),
                id='back_to_strategy_input',
                state=ProjectStates.project_strategy_change,
            ),
        ),
        getter=project_info_getter,
        state=ProjectStates.project_strategy_confirm,
    ),
)


router = Router()

router.include_router(project_dialog)
