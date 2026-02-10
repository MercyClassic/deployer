from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Table,
    func,
)

from deployer.database import metadata

users_table = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('telegram_id', BigInteger, unique=True, nullable=False),
    Column('username', String),
    Column('created_at', DateTime, server_default=func.now()),
    Column('is_active', Boolean, default=True),
)
