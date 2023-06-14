from aiogram.types import Message, InlineKeyboardMarkup, ParseMode

from core.aiobot import MoneybookBot
from core.logging import log
from sql.crud.record import delete_record, read_record, read_record_joined
from utils.message_template import (
    record_deleted_message,
    record_check_delete_message_template,
)
from utils.tools import escape_message, generate_check_delete_buttons

from .base import record_message_pagination


async def bot_delete_record(message: Message, record_id: str) -> None:
    """
    delete limitation
    """
    await delete_record(record_id=record_id)
    await message.edit_text(text=record_deleted_message)
    pass


async def handle_delete_record_callback(message: Message, record_id: str) -> None:
    """
    double check if the user want to delete this record
    """
    inline_keyboard = [generate_check_delete_buttons(id=record_id)]
    record = await read_record_joined(id=record_id)
    log().info(record)
    record_check_delete_message = \
        record_check_delete_message_template.format(
            record_date=escape_message(record.record_date.isoformat()),
            user_name=record.user.name,
            record_type="收入" if record.is_income else "支出",
            category_name=record.category.name,
            amount=record.amount,
            description=escape_message(record.description),
        )
    reply_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    await message.edit_text(
        text=record_check_delete_message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    pass


@MoneybookBot().dp.message_handler(commands=['delete_record'])
async def delete_record_handler(message: Message):
    """
    list user records in this group page 1 for deletion
    """
    await record_message_pagination(
        message=message,
        pagination_type="delete",
        new_page=1,
        reply=True,
    )
    pass
