from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, Boolean, BigInteger, JSON
from database import metadata


users = Table(
    'users',
    metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('email', String, unique=True),
    Column('hashed_password', String),
    Column('created_at', DateTime)
)

devices = Table(
    'devices', 
    metadata, 
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('device_id', String, unique=True),
    Column('name', String),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('token', String, unique=True, nullable=False),
    Column('status', Boolean, nullable=False, default=True),
    Column('created_at', DateTime)
)

measurements = Table(
    'measurements', 
    metadata, 
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('device_id', Integer, ForeignKey('devices.id', ondelete='CASCADE'), nullable=True),
    Column('timestamp', DateTime, index=True),
    Column('metrics', JSON),
    Column('received_at', DateTime)
)