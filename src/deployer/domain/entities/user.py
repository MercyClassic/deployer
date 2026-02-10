from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deployer.domain.entities.project import Project


@dataclass
class User:
    id: int | None = field(init=False)
    telegram_id: int
    username: str | None
    created_at: datetime.datetime | None
    is_active: bool = True
    projects: list[Project] = field(init=False, repr=False)

    @classmethod
    def create(cls, telegram_id: int, username: str | None) -> User:
        return cls(
            telegram_id=telegram_id,
            username=username,
            created_at=None,
            is_active=True,
        )
