from sqlalchemy import event

from deployer.domain.entities.project import ProjectConfig
from deployer.domain.entities.project_configs import CONFIG_TYPE_BY_STRATEGY


def register_project_config_events() -> None:
    def _serialize_config_on_load(target, *args, **kwargs) -> None:
        if isinstance(target.config, dict):
            target.config = CONFIG_TYPE_BY_STRATEGY[target.strategy](**target.config)

    event.listen(ProjectConfig, 'load', _serialize_config_on_load)
    event.listen(ProjectConfig, 'refresh', _serialize_config_on_load)


def register_events() -> None:
    register_project_config_events()
