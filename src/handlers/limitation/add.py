# command triggered: ask period
# callback_query.data get:
#   use message.text to get current limitation configuration
#   update current limitation configuration with data(can be period or category)
# reply text:
#   ensure user exist, group exist, user in group
#   use message.text to get current limitation configuration
#   update current limitation configuration with data(amount)
#   create limitation and send success message to group
from re import Match, search
from typing import Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ParseMode

from core.aiobot import MoneybookBot
from core.logging import log
from sql.crud.category import read_categories
from sql.crud.limitation import create_limitation
from sql.schemas.limitation import NewLimitation
from utils.tools import (
    add_close_button,
    escape_message,
    generate_period_buttons_list,
    get_category_dict,
    get_user_and_group,
    period_show_list,
)
from utils.message_template import (
    limitation_created_message,
    limitation_message_template,
    limitation_row_name_list,
    limitation_question_text_list,
    limitation_undecided_italic_text,
    limitation_undecided_text,
)


async def bot_send_limitation(limitation_raw: str, new_data: Message):
    match: Optional[Match] = search('^[0-9]+', new_data.text)
    if match is None:
        return None
    amount = int(match.group())
    limitation_dict, _, _ = \
        await parse_and_update_limitation(
            message_text=limitation_raw,
            new_data=new_data.text,
        )
    _, group = await get_user_and_group(message=new_data)

    category_dict = await get_category_dict()
    new_limitation = NewLimitation(
        group_id=group.id,
        category_id=category_dict[limitation_dict['category']].id,
        period=period_show_list.index(limitation_dict['period']),
        amount=amount,
    )
    limitation = await create_limitation(new_limitation=new_limitation)
    created_message = limitation_created_message
    await MoneybookBot().bot.send_message(
        chat_id=group.telegram_id,
        text=created_message,
    )
    pass


async def generate_add_limitation_inline_keyboard(status: str) -> Optional[list[list[InlineKeyboardButton]]]:
    inline_keyboard: list[list[InlineKeyboardButton]] = None
    if status == limitation_row_name_list[0]:
        categories = await read_categories()
        category_buttons = [
            InlineKeyboardButton(
                text=category.name,
                callback_data=category.name,
            )
            for category in categories
        ]
        inline_keyboard = []
        category_count = len(category_buttons)
        for idx in range(0, category_count, 5):
            inline_keyboard.append(category_buttons[idx:idx+5])
            pass
        log().info(inline_keyboard)
        pass
    return inline_keyboard


async def handle_limitation_callback(
    message: Message,
    new_data: str,
) -> None:
    """
    parse to get current limitation dict
    check 
    form message(current limitation + question)
    update message
    """
    limitation_dict, new_question, new_inline_keyboard = \
        await parse_and_update_limitation(
            message_text=message.text,
            new_data=new_data,
        )
    new_message = limitation_message_template.format(
        period=limitation_dict['period'],
        category_name=limitation_dict['category'],
        question_text=new_question,
    )
    new_reply_markup = InlineKeyboardMarkup(
        inline_keyboard=add_close_button(new_inline_keyboard))
    await message.edit_text(
        text=new_message,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=new_reply_markup,
    )
    pass


async def parse_and_update_limitation(
    message_text: str, new_data: str
) -> tuple[dict, str, Optional[list[list[InlineKeyboardButton]]]]:
    # get list of limitation field row
    message_row_list = message_text.split('\n')
    inline_keyboard: list[list[InlineKeyboardButton]] = None
    limitation_dict = {}
    question_text: str = None
    row_msg_ques_zip = zip(
        limitation_row_name_list,
        message_row_list,
        limitation_question_text_list[1:],
    )

    for row_name, message_row, question in row_msg_ques_zip:
        _, *data = message_row.split('：')
        cur_data = '：'.join(data)
        if cur_data != limitation_undecided_text:
            field_data = cur_data
            pass
        elif question_text is None:
            field_data = new_data
            question_text = question
            inline_keyboard = await generate_add_limitation_inline_keyboard(status=row_name)
            pass
        else:
            field_data = limitation_undecided_italic_text
            pass
        limitation_dict[row_name] = field_data
        pass

    if question_text is None:
        question_text = limitation_question_text_list[-1]
        pass
    return (limitation_dict, question_text, inline_keyboard)


@MoneybookBot().dp.message_handler(commands=['add_limitation'])
async def add_limitation_handler(message: Message):
    """
    add new limitation in this group. first ask limitation date
    """
    inline_keyboard = generate_period_buttons_list()
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=add_close_button(inline_keyboard))
    reply_text = limitation_message_template.format(
        period=limitation_undecided_italic_text,
        category_name=limitation_undecided_italic_text,
        question_text=limitation_question_text_list[0],
    )
    await message.reply(
        text=reply_text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=reply_markup,
    )
    pass
