from typing import Any

from deployer.domain.validators.annotation import AnnotationValidator


class ProjectConfigType(metaclass=AnnotationValidator):
    def to_dict(self) -> dict:
        return self.__dict__


class ShellConfig(ProjectConfigType):
    commands: list[str]


class GitConfig(ProjectConfigType):
    repository_url: str
    branch: str = 'master'
    with_entrypoint: bool = True


class DockerConfig(ProjectConfigType):
    image: str
    registry_url: str
    volumes: dict[str, str] | None
    ports: list[tuple[str, str]] | None
    network: str | None
    env: dict[str, Any] | None


PROJECT_CONFIG_TYPE = ShellConfig | GitConfig | DockerConfig

CONFIG_TYPE_BY_STRATEGY = {
    'shell': ShellConfig,
    'git': GitConfig,
    'docker': DockerConfig,
}
