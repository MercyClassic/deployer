from sqlalchemy.orm import relationship

from deployer.database import mapper_registry
from deployer.database.events import register_events
from deployer.database.models import (
    deployments_table,
    project_configs_table,
    projects_table,
    servers_table,
    users_table,
)
from deployer.domain.entities.deployment import Deployment
from deployer.domain.entities.project import Project, ProjectConfig, Server
from deployer.domain.entities.user import User


def start_user_mapper() -> None:
    mapper_registry.map_imperatively(
        User,
        users_table,
        properties={
            'projects': relationship(
                Project, back_populates='user', order_by=projects_table.c.id,
            ),
        },
    )


def start_project_mapper() -> None:
    mapper_registry.map_imperatively(
        Project,
        projects_table,
        properties={
            'user': relationship(
                User,
                back_populates='projects',
            ),
            'configs': relationship(
                ProjectConfig,
                back_populates='project',
                cascade='all, delete-orphan',
            ),
            'servers': relationship(
                Server,
                back_populates='project',
                cascade='all, delete-orphan',
            ),
            'deployments': relationship(
                Deployment,
                back_populates='project',
                cascade='all, delete-orphan',
            ),
        },
    )

    mapper_registry.map_imperatively(
        ProjectConfig,
        project_configs_table,
        properties={
            'project': relationship(
                Project,
                back_populates='configs',
            ),
        },
    )

    mapper_registry.map_imperatively(
        Server,
        servers_table,
        properties={
            'project': relationship(
                Project,
                back_populates='servers',
            ),
        },
    )


def start_deployment_mapper() -> None:
    mapper_registry.map_imperatively(
        Deployment,
        deployments_table,
        properties={
            'project': relationship(
                Project,
                back_populates='deployments',
            ),
        },
    )


def start_db_mapping() -> None:
    start_user_mapper()
    start_project_mapper()
    start_deployment_mapper()

    register_events()
