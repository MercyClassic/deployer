from aiogram.fsm.state import State, StatesGroup


class ProjectStates(StatesGroup):
    project_list = State()
    project_menu = State()
    project_info = State()

    project_create = State()
    project_strategy = State()
    project_confirm = State()

    project_strategy_change = State()
    project_strategy_confirm = State()

    config_upload = State()
    config_show = State()
    config_rollback = State()

    servers_list = State()
    server_info = State()

    server_add = State()
    server_host = State()
    server_user = State()
    server_secret = State()
    server_workdir = State()
    server_port = State()
    server_confirm = State()
