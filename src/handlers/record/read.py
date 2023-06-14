from csv import DictWriter
from glob import glob
from os import makedirs, remove
from shutil import copy
from time import time
from uuid import UUID

from aiogram.types import Message, InlineKeyboardMarkup, ParseMode

from core.aiobot import MoneybookBot
from core.logging import log
from sql.crud.record import read_record_joined, read_records_joined
from sql.models.record import Record
from sql.schemas.record import ExtendRecord
from utils.message_template import record_detail_message_template
from utils.tools import add_close_button, escape_message, get_user_and_group

from .base import record_message_pagination


CACHE_TIME = 60 * 60
FIELD_NAME = [
    'group_name', 'group_telegram_id',
    'user_name', 'user_telegram_id',
    'record_date',
    'record_type',
    'category_name',
    'amount',
    'description',
]


async def generate_csv_file(group_id: UUID, record_list: list[ExtendRecord]) -> str:
    dir_path = './file/record'
    makedirs(dir_path, exist_ok=True)
    exist_files = glob(f"{dir_path}/*.csv")
    for exist_file in exist_files:
        exist_file_ts = int(exist_file.removesuffix(".csv").split("_")[1])
        if exist_file.startswith(f"{dir_path}/{group_id}_"):
            if time() - exist_file_ts < CACHE_TIME:
                return exist_file
            else:
                remove(exist_file)
                pass
            pass
        pass
    timestamp = int(time())
    filename = f"/{group_id}_{timestamp}.csv"
    with open(dir_path+filename, 'w') as csv_file:
        writer = DictWriter(csv_file, FIELD_NAME)
        writer.writeheader()
        for record in record_list:
            record_dict = record.dict(include={'amount', 'description'})
            record_dict.update({
                'group_name': record.group.name,
                'group_telegram_id': record.group.telegram_id,
                'user_name': record.user.name,
                'user_telegram_id': record.user.telegram_id,
                'record_date': record.record_date.isoformat(),
                'record_type': '收入' if record.is_income else '支出',
                'category_name': record.category.name,
            })
            writer.writerow(record_dict)
            pass
        pass
    return dir_path+filename


async def handle_download_csv_callback(message: Message) -> None:
    user, group = await get_user_and_group(message=message)
    records = await read_records_joined(
        group_id=group.id,
        order_by_columns=[
            Record.record_date,
            Record.category_id,
            Record.amount,
            Record.description,
        ],
    )
    filename = await generate_csv_file(
        group_id=group.id,
        record_list=records,
    )
    group_filename = f"./{group.name}.csv"
    copy(filename, group_filename)
    with open(group_filename, 'rb') as f:
        await MoneybookBot().bot.send_document(
            chat_id=message.chat.id,
            document=f,
        )
        pass
    remove(group_filename)
    pass


async def handle_read_record_callback(message: Message, record_id: str) -> None:
    """
    double check if the user want to delete this record
    """
    record = await read_record_joined(id=record_id)
    record_check_delete_message = \
        record_detail_message_template.format(
            record_date=escape_message(record.record_date.isoformat()),
            user_name=record.user.name,
            record_type="收入" if record.is_income else "支出",
            category_name=record.category.name,
            amount=record.amount,
            description=escape_message(record.description),
        )
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=add_close_button(inline_keyboard=[])
    )
    await message.edit_text(
        text=record_check_delete_message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    pass


@MoneybookBot().dp.message_handler(commands=['read_record'])
async def read_record_handler(message: Message):
    """
    show group records page 1
    """
    await record_message_pagination(message=message, pagination_type="read", new_page=1, reply=True)
    pass
