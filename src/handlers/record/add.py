from re import Match, search
from typing import Optional
from datetime import date, datetime
from typing import Optional

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ParseMode,
)

from core.aiobot import MoneybookBot
from core.logging import log
from sql.crud.category import read_categories
from sql.crud.record import create_record
from sql.schemas.record import NewRecord
from utils.tools import (
    SPACE,
    add_close_button,
    ensure_user_in_group,
    escape_message,
    generate_date_button_list,
    get_category_dict,
    get_user_and_group,
)
from utils.message_template import (
    record_created_message,
    record_message_template,
    record_row_name_list,
    record_question_text_list,
    record_undecided_italic_text,
    record_undecided_text,
)


async def bot_send_record(record_raw: str, new_data: Message):
    match: Optional[Match] = search('^[0-9]+[ ]?.*', new_data.text)
    if match is None:
        return None
    match_string: str = match.group()
    amount, *description_rows = match_string.split(sep=SPACE)
    description = SPACE.join(description_rows)
    record_dict, _, _ = await parse_and_update_record(
        message_text=record_raw,
        new_data=new_data.text,
    )
    user, group = await get_user_and_group(message=new_data)
    await ensure_user_in_group(user_id=user.id, group=group)

    category_dict = await get_category_dict()
    new_record = NewRecord(
        record_date=date.fromisoformat(record_dict['record_date']),
        user_id=user.id,
        group_id=group.id,
        category_id=category_dict[record_dict['category']].id,
        is_income=record_dict['record_type'] == '收入',
        amount=int(amount),
        description=description,
    )
    record = await create_record(new_record=new_record)
    created_message = record_created_message
    await MoneybookBot().bot.send_message(
        chat_id=group.telegram_id,
        text=created_message,
    )
    pass


async def generate_add_record_inline_keyboard(
    status: str,
) -> list[list[InlineKeyboardButton]]:
    if status == record_row_name_list[0]:
        inline_keyboard = [[
            InlineKeyboardButton(text='收入', callback_data='收入'),
            InlineKeyboardButton(text='支出', callback_data='支出'),
        ]]
        pass
    elif status == record_row_name_list[1]:
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
        pass
    elif status == record_row_name_list[2]:
        inline_keyboard = []
        pass
    return inline_keyboard


async def handle_record_callback(
    message: Message,
    new_data: str,
) -> None:
    """
    parse to get current record dict
    check 
    form message(current record + question)
    update message
    """
    record_dict, new_question, new_inline_keyboard = \
        await parse_and_update_record(
            message_text=message.text,
            new_data=new_data,
        )
    new_message = record_message_template.format(
        record_date=escape_message(record_dict['record_date']),
        record_type=record_dict['record_type'],
        category_name=record_dict['category'],
        question_text=new_question,
    )
    new_reply_markup = InlineKeyboardMarkup(
        inline_keyboard=add_close_button(new_inline_keyboard)
    )
    await message.edit_text(
        text=new_message,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=new_reply_markup,
    )
    pass


async def parse_and_update_record(
    message_text: str, new_data: str
) -> tuple[dict, str, Optional[list[list[InlineKeyboardButton]]]]:
    # get list of record field row
    message_row_list = message_text.split('\n')
    inline_keyboard: list[list[InlineKeyboardButton]] = []
    record_dict = {}
    question_text: str = None
    row_msg_ques_zip = zip(
        record_row_name_list,
        message_row_list,
        record_question_text_list[1:],
    )

    for row_name, message_row, question in row_msg_ques_zip:
        _, *data = message_row.split('：')
        cur_data = '：'.join(data)
        if cur_data != record_undecided_text:
            field_data = cur_data
            pass
        elif question_text is None:
            field_data = new_data
            question_text = question
            inline_keyboard = \
                await generate_add_record_inline_keyboard(status=row_name)
            pass
        else:
            field_data = record_undecided_italic_text
            pass
        record_dict[row_name] = field_data
        pass

    if question_text is None:
        question_text = record_question_text_list[-1]
        pass
    return (record_dict, question_text, inline_keyboard)


@MoneybookBot().dp.message_handler(commands=['add_record'])
async def add_record_handler(message: Message):
    """
    add new record in this group. first ask record date
    """
    inline_keyboard = [
        generate_date_button_list(base_date=datetime.today())
    ]
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=add_close_button(inline_keyboard)
    )
    reply_text = record_message_template.format(
        record_date=record_undecided_italic_text,
        record_type=record_undecided_italic_text,
        category_name=record_undecided_italic_text,
        question_text=record_question_text_list[0],
    )
    await message.reply(
        text=reply_text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=reply_markup,
    )
    pass


@MoneybookBot().dp.message_handler(commands=['fast_record'])
async def fast_record_handler(message: Message):
    """
    add new record with default value of record date, type, category,
    then ask amount and description
    """
    record_dict = {
        'record_date': date.today().strftime('%Y-%m-%d'),
        'record_type': '支出',
        'category': '餐費',
    }
    new_question = record_question_text_list[-1]
    new_message = record_message_template.format(
        record_date=escape_message(record_dict['record_date']),
        record_type=record_dict['record_type'],
        category_name=record_dict['category'],
        question_text=new_question,
    )
    close_markup = InlineKeyboardMarkup(
        inline_keyboard=add_close_button([]),
    )
    await message.reply(
        text=new_message,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=close_markup,
    )
    pass
