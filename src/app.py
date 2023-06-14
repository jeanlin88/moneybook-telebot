from asyncio import get_event_loop

from aiogram import executor
from fastapi import FastAPI

from config.settings import Settings
from core.aiobot import MoneybookBot
from core.logging import init_logger, log
from handlers import *


def start_app():
    init_logger()
    if Settings().app.autostart:
        MoneybookBot().start()
    pass


def stop_app():
    MoneybookBot().stop()
    pass


app = FastAPI(on_startup=[start_app], on_shutdown=[stop_app])

@app.get('/api/v1/bot/start')
async def start_telegram_bot():
    MoneybookBot().start()
    pass

@app.get('/api/v1/bot/stop')
async def stop_telegram_bot():
    MoneybookBot().stop()
    pass


if __name__ == '__main__':
    init_logger()
    log().info("start polling")
    loop = get_event_loop()
    loop.run_until_complete(MoneybookBot().say_hi())
    executor.start_polling(MoneybookBot().dp, skip_updates=True)
    loop.run_until_complete(MoneybookBot().say_bye())
