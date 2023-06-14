from asyncio import new_event_loop
from threading import Event, Thread

from aiogram import Bot, Dispatcher, types

from config.settings import Settings
from core.logging import log
from sql.crud.group import read_groups_joined
from .singleton import Singleton


class MoneybookBot(metaclass=Singleton):
    def __init__(self):
        token = Settings().bot.token
        self.telegram_id = token.split(':')[0]
        self.bot = Bot(token=token)
        self.name = Settings().bot.name
        self.dp = Dispatcher(self.bot)
        self.__running__ = Event()
        pass

    def __thread_target__(self) -> None:
        loop = new_event_loop()
        log().debug("before say hi")
        loop.run_until_complete(self.say_hi())
        log().debug("before start polling")
        loop.run_until_complete(self.dp.start_polling())
        log().debug("before say bye")
        loop.run_until_complete(self.say_bye())
        pass

    def start(self) -> None:
        log().debug('in start, running: %s', self.__running__.is_set())
        if not self.__running__.is_set():
            log().debug('about to start thread')
            self.__running__.set()
            self.__thread__ = Thread(target=self.__thread_target__)
            self.__thread__.start()
            log().debug('thread start')
            pass
        pass

    def stop(self) -> None:
        log().debug('in stop, running: %s', self.__running__.is_set())
        if self.__running__.is_set():
            log().debug('about to join thread')
            self.__running__.clear()
            log().debug('before stop polling')
            self.dp.stop_polling()
            log().debug('after stop polling')
            self.__thread__.join()
            log().debug('after join')
            del self.__thread__
            log().debug('thread delete')
            pass
        pass

    async def say_hi(self) -> None:
        groups = await read_groups_joined()
        for group in groups:
            if group.telegram_id != group.admin_user.telegram_id:
                await self.bot.send_message(chat_id=group.telegram_id, text="I'm up!")
                pass
            pass
        pass

    async def say_bye(self) -> None:
        groups = await read_groups_joined()
        for group in groups:
            if group.telegram_id != group.admin_user.telegram_id:
                await self.bot.send_message(chat_id=group.telegram_id, text="shutdown...")
                pass
            pass
        pass