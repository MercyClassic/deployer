from typing import Annotated

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from deployer.database.identity_provider import IdentityProviderInterface
from deployer.domain.exceptions.user import UserNotFound
from deployer.presentators.tg.states.project import ProjectStates
from deployer.presentators.tg.states.user import UserStates


@inject
async def on_projects_click(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    identity_provider: Annotated[IdentityProviderInterface, FromDishka('identity')],
) -> None:
    try:
        await identity_provider.get_user()
    except UserNotFound:
        await callback.answer(
            '❌ Вы не зарегистрированы. Нажмите «Зарегистрироваться» в профиле',
            show_alert=True,
        )
        await manager.start(UserStates.main_menu, mode=StartMode.NORMAL)
        return

    await manager.start(ProjectStates.project_list, mode=StartMode.NORMAL)
