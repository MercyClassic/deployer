from contextlib import suppress

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ErrorEvent

router = Router()


@router.error()
async def handle_errors(event: ErrorEvent) -> None:
    message = f'❌ Возникла ошибка: {event.exception!s}'
    with suppress(TelegramBadRequest):
        if event.update.message:
            await event.update.message.answer(message)
        elif event.update.callback_query:
            await event.update.callback_query.answer(message)
