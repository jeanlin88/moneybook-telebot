from aiogram.types import Message, ParseMode

from core.aiobot import MoneybookBot
from core.logging import log
from utils.message_template import hello_message_template
from utils.tools import escape_message, get_user_and_group


@MoneybookBot().dp.message_handler(commands=['start'])
async def start_handler(message: Message):
    log().info(message)
    user, group = await get_user_and_group(message=message)
    hello_message = hello_message_template.format(
        user_name=user.name,
        user_telegram_id=user.telegram_id,
        group_name=group.name,
        bot_name=MoneybookBot().name,
        bot_telegram_id=MoneybookBot().telegram_id,
    )
    await message.reply(
        text=hello_message,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    pass
