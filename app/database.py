from pathlib import Path
from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.orm import sessionmaker


database_path = Path(__file__).resolve().parents[1]/"sensor.db"
engine = create_engine(f'sqlite:///{database_path}')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()


def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def initialize_database():
    with engine.begin() as connection:
        metadata.create_all(connection)


@event.listens_for(engine, "connect")
def set_sqlite_pragrma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()