from __future__ import annotations

import datetime
import enum
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deployer.domain.entities.project import Project


class DeploymentStatus(enum.StrEnum):
    pending = 'pending'
    running = 'running'
    success = 'success'
    failed = 'failed'


@dataclass
class Deployment:
    id: int | None = field(init=False)
    project_id: int
    status: DeploymentStatus
    started_at: datetime.datetime | None
    std: str | None
    finished_at: datetime.datetime | None
    project: Project | None = field(init=False, repr=False)

    @classmethod
    def create(cls, project_id: int, status: DeploymentStatus) -> Deployment:
        return cls(
            project_id=project_id,
            status=status,
            started_at=None,
            std=None,
            finished_at=None,
        )

    def set_std(self, std: str) -> None:
        self.std = std

    def set_status(self, status: DeploymentStatus) -> None:
        self.status = status

    def set_finished_at(self) -> None:
        self.finished_at = datetime.datetime.now(datetime.UTC)
