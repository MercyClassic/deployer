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


@router.message(Command(commands=['help', 'menu', 'start']))
async def start_command(
    message: types.Message,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        EntryStates.main_menu,
        show_mode=ShowMode.EDIT,
        mode=StartMode.RESET_STACK,
    )


router.include_router(entry_dialog)
