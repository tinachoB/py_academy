"""
Helper for the MySql connection
"""
import sqlalchemy
import sqlalchemy.orm as orm

from server.common.env_variables import get_env_vars

_DATABASE_URL_PATTERN = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}"

engine = sqlalchemy.create_engine(_DATABASE_URL_PATTERN.format(**get_env_vars().mysql._asdict()))
SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
ModelBase = orm.declarative_base()
ModelBase.metadata.create_all(bind=engine)


def get_db() -> None:  # type: ignore[misc]
    """
    Get the current database instance based on the initial configuration
    :return: None
    """
    db_instance = None
    try:
        db_instance = SessionLocal()
        yield db_instance
    finally:
        if db_instance is not None:
            db_instance.close()
