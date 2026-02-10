from aiogram import Router
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Cancel
from aiogram_dialog.widgets.text import Const, Format

from deployer.presentators.tg.handlers.user import (
    on_register_click,
    user_data_getter,
)
from deployer.presentators.tg.states.user import UserStates

user_dialog = Dialog(
    Window(
        Format(
            '👤 Профиль пользователя\n\n'
            'Имя: {username}\n'
            'Telegram ID: {event.from_user.id}\n'
            'Статус: {status}\n'
            'Дата регистрации: {registration_date}',
        ),
        Button(
            Const('📋 Зарегистрироваться'),
            id='register',
            on_click=on_register_click,
            when='not_registered',
        ),
        Cancel(Const('🔙 Назад')),
        getter=user_data_getter,
        state=UserStates.main_menu,
    ),
)

router = Router()

router.include_router(user_dialog)
