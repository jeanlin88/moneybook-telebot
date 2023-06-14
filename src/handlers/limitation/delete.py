from aiogram.types import Message, InlineKeyboardMarkup, ParseMode

from core.aiobot import MoneybookBot
from core.logging import log
from sql.crud.limitation import delete_limitation, read_limitation, read_limitation_joined
from utils.message_template import (
    limitation_check_delete_message_template,
    limitation_deleted_message,
)
from utils.tools import (
    generate_check_delete_buttons,
    get_category_dict,
    period_show_list,
)

from .base import limitation_message_pagination


async def bot_delete_limitation(message: Message, limitation_id: str) -> None:
    """
    delete limitation
    """
    await delete_limitation(limitation_id=limitation_id)
    await message.edit_text(text=limitation_deleted_message)
    pass


async def handle_delete_limitation_callback(message: Message, limitation_id: str) -> None:
    """
    double check if the user want to delete this limitation
    """
    inline_keyboard = [generate_check_delete_buttons(id=limitation_id)]
    limitation = await read_limitation_joined(id=limitation_id)
    log().info(limitation)
    limitation_check_delete_message = \
        limitation_check_delete_message_template.format(
            period=period_show_list[limitation.period],
            category_name=limitation.category.name,
            amount=limitation.amount,
        )
    reply_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    await message.edit_text(
        text=limitation_check_delete_message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    pass


@MoneybookBot().dp.message_handler(commands=['delete_limitation'])
async def delete_limitation_handler(message: Message):
    """
    list limitation in this group for deletion
    """
    await limitation_message_pagination(message=message, reply=True)
    pass
