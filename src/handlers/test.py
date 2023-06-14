from aiogram.types import Message, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup

from core.aiobot import MoneybookBot
from utils.tools import escape_message


TESTING = """\
1. longlong還有中文
2022-10-24  支出 餐費 123

2. testing
2022-10-11  支出 餐費 111

3. testing
2022-10-11  支出 餐費 111

4. testing
2022-10-11  支出 餐費 111

5. testing
2022-10-11  支出 餐費 111
"""
TESTING="""\
[Jean Lin](tg://user?id=1880329022)
joined groups:
    `Jean Lin`
"""


@MoneybookBot().dp.message_handler(commands=["test"])
async def test_message(message: Message) -> None:
    test_msg = TESTING
    test_reply = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1", callback_data="record 1"),
                InlineKeyboardButton(text="2", callback_data="record 2"),
                InlineKeyboardButton(text="3", callback_data="record 3"),
                InlineKeyboardButton(text="4", callback_data="record 4"),
                InlineKeyboardButton(text="5", callback_data="record 5"),
            ],
            [
                InlineKeyboardButton(text="<<", callback_data=1),
                InlineKeyboardButton(text="<", callback_data=1),
                InlineKeyboardButton(text="1", callback_data=1),
                InlineKeyboardButton(text=">", callback_data=2),
                InlineKeyboardButton(text=">>", callback_data=3),
            ],
            [
                InlineKeyboardButton(text="close", callback_data="close"),
            ]
        ]
    )
    await message.reply(
        text=test_msg,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=test_reply,
    )