from abc import ABC, abstractmethod

from deployer.database.repositories.user import UserRepository
from deployer.domain.entities.user import User
from deployer.domain.exceptions.user import UserNotFound


class IdentityProviderInterface(ABC):
    telegram_id: int

    @abstractmethod
    async def get_user(self) -> User:
        raise NotImplementedError


class IdentityProvider(IdentityProviderInterface):
    def __init__(self, telegram_id: int, user_repo: UserRepository):
        self._telegram_id = telegram_id
        self._user_repo = user_repo

    async def get_user(self) -> User:
        user = await self._user_repo.get_by_telegram_id(self._telegram_id)
        if not user:
            raise UserNotFound
        return user
