from aiogram.types import Message, InlineKeyboardMarkup, ParseMode

from core.aiobot import MoneybookBot
from sql.crud.limitation import read_limitations, read_limitations_joined
from utils.tools import add_close_button, escape_message, get_user_and_group, generate_seq_buttons_list

from .draft import caculate_summaries, generate_summary_message


@MoneybookBot().dp.message_handler(commands=['summary'])
async def summary_handler(message: Message):
    """
    caculate
    """
    user, group = await get_user_and_group(message=message)
    limitation_list = await read_limitations_joined(group_id=group.id)
    limitation_id_list = [limitation.id for limitation in limitation_list]
    summary_list = await caculate_summaries(limitation_list=limitation_list)
    summary_message = await generate_summary_message(summary_list=summary_list)
    summary_inline_keyboard = generate_seq_buttons_list(
        id_list=limitation_id_list,
        base=0,
    )
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=add_close_button([summary_inline_keyboard]))
    await message.reply(
        text=summary_message,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=reply_markup,
    )
