from typing import Annotated

from aiogram.types import TelegramObject
from dishka import FromComponent, Scope, provide
from dishka.integrations.aiogram import AiogramProvider

from deployer.database.identity_provider import (
    IdentityProvider,
    IdentityProviderInterface,
)
from deployer.database.repositories.user import UserRepository


class TelegramIdentityProvider(AiogramProvider):
    scope = Scope.REQUEST
    component = 'identity'
    DB_COMPONENT = 'db'

    @provide
    async def get_identity_provider(
        self,
        event: TelegramObject,
        user_repo: Annotated[UserRepository, FromComponent(DB_COMPONENT)],
    ) -> IdentityProviderInterface:
        return IdentityProvider(telegram_id=event.from_user.id, user_repo=user_repo)
