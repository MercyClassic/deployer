from deployer.database.repositories.user import UserRepository
from deployer.database.transaction import TransactionManagerInterface
from deployer.domain.entities.user import User


class CreateUserInteractor:
    def __init__(
        self,
        transaction_manager: TransactionManagerInterface,
        user_repo: UserRepository,
    ):
        self._transaction_manager = transaction_manager
        self._user_repo = user_repo

    async def execute(self, telegram_id: int, username: str | None) -> User:
        user = User.create(telegram_id=telegram_id, username=username)
        user = await self._user_repo.create(user)
        await self._transaction_manager.commit()
        return user
