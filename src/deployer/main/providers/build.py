from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiogram import AiogramProvider

from deployer.main.providers.db import DbProvider
from deployer.main.providers.identity import TelegramIdentityProvider
from deployer.main.providers.interactor import InteractorProvider


def build_container() -> AsyncContainer:
    return make_async_container(
        DbProvider(),
        TelegramIdentityProvider(),
        InteractorProvider(),
        AiogramProvider(),
    )
