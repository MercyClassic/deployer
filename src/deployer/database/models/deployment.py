from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    func,
)

from deployer.database import metadata

deployments_table = Table(
    'deployments',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('project_id', Integer, ForeignKey('projects.id'), nullable=False),
    Column('status', String, nullable=False),
    Column('started_at', DateTime, nullable=False, server_default=func.now()),
    Column('std', Text),
    Column('finished_at', DateTime),
)
