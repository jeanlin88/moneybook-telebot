from typing import Literal

from aiogram.utils.exceptions import MessageNotModified
from aiogram.types import InlineKeyboardMarkup, Message, ParseMode, InlineKeyboardButton

from core.logging import log
from sql.crud.record import read_records_joined
from sql.models.record import Record
from sql.schemas.record import ExtendRecord
from utils.tools import (
    add_close_button,
    escape_message,
    generate_page_button_list,
    generate_seq_buttons_list,
    get_user_and_group,
)

from utils.message_template import (
    record_not_found_italic_message,
    record_page_read_message_template,
)


async def generate_record_information(record_list: list[ExtendRecord], page: int) -> str:
    log().info("page: %s", page)
    record_info_list = [
        record_page_read_message_template.format(
            seq=(5 * (page - 1) + 1 + record_list.index(record)),
            description=escape_message(record.description),
            record_date=escape_message(record.record_date.isoformat()),
            record_type="收入" if record.is_income else "支出",
            category_name=record.category.name,
            amount=record.amount,
            user_name=record.user.name,
            user_telegram_id=record.user.telegram_id,
        )
        for record in record_list
    ]
    record_infomation = '\n'.join(record_info_list)
    return record_infomation


async def generate_new_record_page(
    message: Message,
    record_list: list[ExtendRecord],
    page: int,
    reply: bool,
) -> None:
    """
    generate record_information
    generate page buttons
    check message modified
    send or reply to message
    """
    if record_list:
        page_button_list = generate_page_button_list(base_page=page)
        message_text = await generate_record_information(record_list=record_list, page=page)
        seq_button_list = generate_seq_buttons_list(
            id_list=[record.id for record in record_list],
            base=5 * (page - 1),
        )
        inline_keyboard = [
            seq_button_list,
            page_button_list,
            [InlineKeyboardButton(text="下載csv", callback_data="csv")],
        ]
        pass
    else:
        message_text = record_not_found_italic_message
        inline_keyboard = []
        pass
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=add_close_button(inline_keyboard),
    )
    try:
        if reply:
            await message.reply(
                text=message_text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=reply_markup,
            )
            pass
        else:
            await message.edit_text(
                text=message_text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=reply_markup,
            )
            pass
        pass
    except MessageNotModified as ex:
        pass
    pass


async def record_message_pagination(
    message: Message,
    pagination_type: Literal['read', 'edit', 'delete'],
    new_page: int,
    reply: bool = False
) -> None:
    """
    get record_list by pagination_type & new_page
    call generate new record page with reply=False to edit message
    """
    log().info("message: %s", message)
    user, group = await get_user_and_group(message=message)
    record_list = []
    if pagination_type == 'read':
        record_list = await read_records_joined(
            group_id=group.id,
            limit=5,
            offset=5 * (new_page - 1),
            order_by_columns=[
                Record.record_date.desc(),
                Record.category_id,
                Record.amount,
                Record.description,
            ],
        )
        pass
    else:
        record_list = await read_records_joined(
            group_id=group.id,
            user_id=user.id,
            limit=5,
            offset=5 * (new_page - 1),
            order_by_columns=[Record.record_date.desc()],
        )
        pass
    await generate_new_record_page(
        message=message,
        record_list=record_list,
        page=new_page,
        reply=reply,
    )
    pass
