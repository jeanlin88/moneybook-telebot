from typing import Literal

from aiogram.types import InlineKeyboardMarkup, Message, ParseMode

from core.logging import log
from sql.crud.limitation import read_limitations_joined
from sql.schemas.limitation import ExtendLimitation
from utils.tools import (
    add_close_button,
    generate_seq_buttons_list,
    get_user_and_group,
    period_show_list,
)
from utils.message_template import (
    limitation_not_found_italic_message,
    limitation_page_read_message_template,
)


async def generate_limitation_information(limitation_list: list[ExtendLimitation]) -> str:
    limitation_info_list = []
    for limitation in limitation_list:
        p_amount, p_unit = period_show_list[limitation.period].split(' ')
        period_formatted = f"{p_amount} {p_unit.rjust(5)}"
        limitation_info = limitation_page_read_message_template.format(
            seq=(1 + limitation_list.index(limitation)),
            period=period_formatted,
            category_name=limitation.category.name,
            amount=limitation.amount,
        )
        limitation_info_list.append(limitation_info)
        pass
    limitation_infomation = '\n'.join(limitation_info_list)
    return limitation_infomation


async def generate_new_limitation_page(
    message: Message,
    limitation_list: list[ExtendLimitation],
    reply: bool,
) -> None:
    """
    generate limitation_information
    check message modified
    send or reply to message
    """
    seq_button_list = []
    if limitation_list:
        message_text = \
            await generate_limitation_information(limitation_list=limitation_list)
        seq_button_list = generate_seq_buttons_list(
            id_list=[limitation.id for limitation in limitation_list],
            base=0,
        )
        inline_keybord = [seq_button_list]
        pass
    else:
        message_text = limitation_not_found_italic_message
        inline_keybord = []
        pass
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=add_close_button(inline_keybord),
    )
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


async def limitation_message_pagination(
    message: Message,
    reply: bool = False
) -> None:
    """
    get limitation_list
    """
    log().info("message: %s", message)
    user, group = await get_user_and_group(message=message)
    limitation_list = await read_limitations_joined(group_id=group.id)
    await generate_new_limitation_page(
        message=message,
        limitation_list=limitation_list,
        reply=reply,
    )
    pass
