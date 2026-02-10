from aiogram.fsm.state import State, StatesGroup


class DeploymentStates(StatesGroup):
    deployment_list = State()
    deployment_logs = State()
    deployment_run = State()
