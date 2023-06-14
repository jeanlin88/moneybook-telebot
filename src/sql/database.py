from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import Settings


class Database(object):
    def __init__(self) -> None:
        self.settings = Settings().database
        pass

    def __init_connection__(self) -> None:
        db_url = "postgresql+asyncpg://{username}:{password}@{host}/{name}".format(
            username=self.settings.username,
            password=self.settings.password,
            host=self.settings.host,
            name=self.settings.name,
        )
        self.engine = create_async_engine(db_url, echo=True)
        self.session_maker = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        pass


__instance__ = {
    "database": None,
}


def get_session_maker() -> sessionmaker:
    if __instance__["database"] is None:
        database = Database()
        database.__init_connection__()
        __instance__["database"] = database
        pass
    database = __instance__["database"]
    return database.session_maker


Base = declarative_base()