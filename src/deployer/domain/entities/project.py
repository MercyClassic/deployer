from __future__ import annotations

import datetime
import enum
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from deployer.domain.entities.project_configs import (
    CONFIG_TYPE_BY_STRATEGY,
    PROJECT_CONFIG_TYPE,
)
from deployer.domain.exceptions.project import (
    ActiveConfigNotFound,
    InvalidConfigFormat,
    InvalidDeployStrategy,
)

if TYPE_CHECKING:
    from deployer.domain.entities.deployment import Deployment
    from deployer.domain.entities.user import User


class DeployStrategy(enum.StrEnum):
    shell = 'shell'
    docker = 'docker'
    git = 'git'


@dataclass
class Project:
    id: int | None = field(init=False)
    user_id: int
    name: str
    deploy_strategy: DeployStrategy
    created_at: datetime.datetime | None
    configs: list[ProjectConfig] = field(init=False, repr=False)
    servers: list[Server] = field(init=False, repr=False)
    deployments: list[Deployment] = field(init=False, repr=False)
    user: User | None = field(init=False, repr=False)

    @classmethod
    def create(cls, user_id: int, name: str, deploy_strategy: str) -> Project:
        try:
            deploy_strategy = DeployStrategy(deploy_strategy)
        except ValueError:
            raise InvalidDeployStrategy
        return cls(
            user_id=user_id,
            name=name,
            deploy_strategy=deploy_strategy,
            created_at=None,
        )

    @property
    def active_config(self) -> ProjectConfig:
        try:
            return next(
                filter(
                    lambda x: x.is_active is True
                    and x.strategy == self.deploy_strategy,
                    self.configs,
                ),
            )
        except StopIteration:
            raise ActiveConfigNotFound

    def set_deploy_strategy(self, strategy: str) -> None:
        try:
            self.deploy_strategy = DeployStrategy(strategy)
        except ValueError:
            raise InvalidDeployStrategy


@dataclass
class ProjectConfig:
    id: int | None = field(init=False)
    project_id: int
    version: int
    config: PROJECT_CONFIG_TYPE
    strategy: DeployStrategy
    created_at: datetime.datetime | None
    is_active: bool
    project: Project | None = field(init=False, repr=False)

    @classmethod
    def create(
        cls,
        project_id: int,
        version: int,
        config: dict,
        strategy: DeployStrategy,
    ) -> ProjectConfig:
        try:
            formatted_config = CONFIG_TYPE_BY_STRATEGY[strategy](**config)
        except ValueError:
            raise InvalidConfigFormat
        return cls(
            project_id=project_id,
            version=version,
            config=formatted_config,
            strategy=strategy,
            created_at=None,
            is_active=True,
        )

    def set_active(self) -> None:
        self.is_active = True

    def set_inactive(self) -> None:
        self.is_active = False


@dataclass
class Server:
    id: int | None = field(init=False)
    project_id: int
    name: str | None
    host: str
    port: int
    ssh_user: str
    ssh_secret: str
    workdir: str
    created_at: datetime.datetime | None
    project: Project | None = field(init=False, repr=False)

    @classmethod
    def create(
        cls,
        project_id: int,
        name: str,
        host: str,
        ssh_user: str,
        ssh_secret: str,
        workdir: str,
        port: int = 22,
    ) -> Server:
        return cls(
            project_id=project_id,
            name=name,
            host=host,
            port=port,
            ssh_user=ssh_user,
            ssh_secret=ssh_secret,
            workdir=workdir,
            created_at=None,
        )
