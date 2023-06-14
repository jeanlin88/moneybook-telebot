# https://fastapi.tiangolo.com/advanced/settings/
from pydantic import BaseSettings


class Settings():
    class SettingsDoc(BaseSettings):
        class SettingsApp(BaseSettings):
            debug: bool
            autostart: bool
            pass

        class SettingsBot(BaseSettings):
            name: str
            token: str
            pass

        class SettingsDatabase(BaseSettings):
            host: str
            username: str
            password: str
            name: str
            pass

        app: SettingsApp
        bot: SettingsBot
        database: SettingsDatabase
        pass

    def __init__(self) -> None:
        self.reload()
        pass

    @property
    def app(self) -> SettingsDoc.SettingsApp:
        return self.__settings__.app

    @property
    def bot(self) -> SettingsDoc.SettingsBot:
        return self.__settings__.bot

    @property
    def database(self) -> SettingsDoc.SettingsDatabase:
        return self.__settings__.database

    def reload(self) -> None:
        from logging import info
        info(self)
        self.__settings__: Settings.SettingsDoc = \
            Settings.SettingsDoc.parse_file('./settings.json')
        pass