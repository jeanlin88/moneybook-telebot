from aiogram.types import Message, InlineKeyboardMarkup, ParseMode

from core.aiobot import MoneybookBot
from core.logging import log
from sql.crud.limitation import read_limitation_joined
from utils.message_template import limitation_detail_message_template
from utils.tools import add_close_button, period_show_list

from .base import limitation_message_pagination


async def handle_read_limitation_callback(message: Message, limitation_id: str) -> None:
    """
    double check if the user want to delete this limitation
    """
    limitation = await read_limitation_joined(id=limitation_id)
    limitation_check_delete_message = \
        limitation_detail_message_template.format(
            period=period_show_list[limitation.period],
            category_name=limitation.category.name,
            amount=limitation.amount,
        )
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=add_close_button(inline_keyboard=[])
    )
    await message.edit_text(
        text=limitation_check_delete_message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    pass


@MoneybookBot().dp.message_handler(commands=['read_limitation'])
async def read_limitation_handler(message: Message):
    """
    show group limitations
    """
    await limitation_message_pagination(message=message, reply=True)
    pass
