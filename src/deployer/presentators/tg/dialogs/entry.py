from aiogram import Router, types
from aiogram.filters import Command
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, Start
from aiogram_dialog.widgets.text import Const

from deployer.presentators.tg.handlers.entry import on_projects_click
from deployer.presentators.tg.states.entry import EntryStates
from deployer.presentators.tg.states.user import UserStates

entry_dialog = Dialog(
    Window(
        Const('🤖 Добро пожаловать в Deployer Bot!\n\nВыберите раздел:'),
        Row(
            Button(
                Const('📁 Проекты'),
                id='projects',
                on_click=on_projects_click,
            ),
            Start(
                Const('👤 Профиль'),
                id='profile',
                state=UserStates.main_menu,
            ),
        ),
        Cancel(Const('❌ Закрыть')),
        state=EntryStates.main_menu,
    ),
)

router = Router()


@router.message(Command(commands=['menu', 'start']))
async def start_command(
    message: types.Message,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        EntryStates.main_menu,
        show_mode=ShowMode.EDIT,
        mode=StartMode.RESET_STACK,
    )


HELP_TEXT = """
🤖 <b>Deployer Bot</b>

Бот для деплоя проектов на удалённые серверы через SSH.

<b>Команды:</b>
/start — главное меню
/help — это сообщение
/deploy &lt;project_id&gt; — запустить деплой проекта

<b>Стратегии деплоя:</b>

<b>Shell</b> — выполняет команды на сервере
<code>{
  "commands": [
    "cd /app",
    "git pull",
    "systemctl restart myapp"
  ]
}</code>

<b>Git</b> — клонирует репозиторий
<code>{
  "repository_url": "https://github.com/user/repo",
  "branch": "main",
  "with_entrypoint": true
}</code>

<b>Docker</b> — пуллит и запускает контейнер
<code>{
  "image": "myapp:latest",
  "registry_url": "registry.example.com",
  "ports": [["8080", "80"]],
  "volumes": {"/host/data": "/container/data"},
  "network": "mynetwork",
  "env": {"DEBUG": "false", "PORT": "8080"}
}</code>

<i>volumes, ports, network, env — опциональны, можно передать null</i>
"""


@router.message(Command('help'))
async def help_handler(message: types.Message) -> None:
    await message.answer(HELP_TEXT, parse_mode='HTML')


router.include_router(entry_dialog)
