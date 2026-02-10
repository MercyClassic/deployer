from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
    func,
)

from deployer.database import metadata
from deployer.database.types.encrypted_string import (
    EncryptedString,
    EncryptedWithToDictMethod,
)
from deployer.domain.entities.project import DeployStrategy

projects_table = Table(
    'projects',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('name', String, nullable=False),
    Column(
        'deploy_strategy',
        Enum(DeployStrategy, name='deploy_strategy', native_enum=True),
        nullable=False,
    ),
    Column('created_at', DateTime, server_default=func.now()),
    UniqueConstraint('user_id', 'name'),
)


project_configs_table = Table(
    'project_configs',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('project_id', Integer, ForeignKey('projects.id'), nullable=False),
    Column('version', Integer, nullable=False),
    Column('config', EncryptedWithToDictMethod, nullable=False),
    Column('strategy', String, nullable=False),
    Column('created_at', DateTime, nullable=False, server_default=func.now()),
    Column('is_active', Boolean, nullable=False),
)


servers_table = Table(
    'servers',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('project_id', Integer, ForeignKey('projects.id'), nullable=False),
    Column('name', String, nullable=False),
    Column('host', String, nullable=False),
    Column('port', Integer, nullable=False),
    Column('ssh_user', String, nullable=False),
    Column('ssh_secret', EncryptedString, nullable=False),
    Column('workdir', String, nullable=False),
    Column('created_at', DateTime, nullable=False, server_default=func.now()),
)
