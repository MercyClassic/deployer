from typing import Annotated

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from deployer.application.interactors.user.create_user import CreateUserInteractor
from deployer.database.identity_provider import (
    IdentityProviderInterface,
)
from deployer.domain.exceptions.user import UserNotFound
from deployer.presentators.tg.states.user import UserStates


@inject
async def on_register_click(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    create_user_interactor: FromDishka[CreateUserInteractor],
):
    user = callback.from_user

    await create_user_interactor.execute(
        username=user.username,
        telegram_id=user.id,
    )

    await callback.answer('✅ Вы успешно зарегистрированы!')
    await manager.switch_to(UserStates.main_menu)


@inject
async def user_data_getter(
    dialog_manager: DialogManager,
    identity_provider: Annotated[IdentityProviderInterface, FromDishka('identity')],
    **kwargs,
) -> dict:
    try:
        user = await identity_provider.get_user()
    except UserNotFound:
        user = None

    return {
        'user': user,
        'not_registered': not bool(user),
        'username': user.username if user else '—',
        'status': ('✅ Зарегистрирован' if bool(user) else '❌ Не зарегистрирован'),
        'registration_date': (user.created_at.strftime('%d.%m.%Y') if user else '—'),
    }
