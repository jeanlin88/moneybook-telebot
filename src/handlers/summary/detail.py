from csv import DictWriter
from datetime import date, timedelta
from glob import glob
from os import makedirs, remove
from shutil import copy
from time import time
from uuid import UUID

from aiogram.types import Message, ParseMode, InlineKeyboardMarkup
from core.aiobot import MoneybookBot

from core.logging import log
from sql.crud.group_membership import read_group_memberships_joined
from sql.crud.limitation import read_limitation, read_limitation_joined
from sql.crud.record import read_records_joined
from sql.models.record import Record
from sql.schemas.limitation import ExtendLimitation
from sql.schemas.record import SummaryUserDetail
from utils.message_template import (
    summary_user_detail_empty_template,
    summary_detail_message_template,
    summary_user_detail_template,
    summary_detail_user_message_template,
)
from utils.tools import (
    add_close_button,
    caculate_start_date_by_period,
    escape_message,
    get_user_and_group,
    month_manipulate,
    period_show_list,
)

from .draft import caculate_summaries


CACHE_TIME = 60 * 60
FIELD_NAME = [
    'record_date',
    'amount',
    'description',
]


async def generate_csv_file(
    limitation: ExtendLimitation,
    summary_user_detail: SummaryUserDetail,
) -> str:
    dir_path = './file/summary'
    makedirs(dir_path, exist_ok=True)
    exist_files = glob(f"{dir_path}/*.csv")
    for exist_file in exist_files:
        exist_file_ts = int(exist_file.removesuffix(".csv").split("_")[2])
        if exist_file.startswith(f"{dir_path}/{limitation.id}_{summary_user_detail.user.id}_"):
            if time() - exist_file_ts < CACHE_TIME:
                return exist_file
            else:
                remove(exist_file)
                pass
            pass
        pass
    timestamp = int(time())
    filename_fields = [
        str(limitation.id),
        str(summary_user_detail.user.id),
        str(timestamp),
    ]
    filename = f"/{'_'.join(filename_fields)}.csv"
    with open(dir_path+filename, 'w') as csv_file:
        writer = DictWriter(csv_file, FIELD_NAME)
        writer.writeheader()
        for record in summary_user_detail.record_list:
            sign = '+' if record.is_income else '-'
            summary_dict = {
                'record_date': record.record_date.isoformat(),
                'amount': sign+str(record.amount),
                'description': record.description,
            }
            writer.writerow(summary_dict)
            pass
        pass
    return dir_path+filename


async def caculate_summary_details(
    group_id: UUID,
    limitation_id: UUID,
) -> list[SummaryUserDetail]:
    limitation = await read_limitation(limitation_id=limitation_id)
    group_membership_list = \
        await read_group_memberships_joined(group_id=group_id)
    group_member_list = [
        group_membership.user
        for group_membership in group_membership_list
    ]
    before_date = date.today()
    after_date = caculate_start_date_by_period(period=limitation.period)
    summary_user_detail_list = []
    for member in group_member_list:
        records = await read_records_joined(
            category_ids=[limitation.category_id],
            date_after=after_date,
            date_before=before_date,
            group_id=group_id,
            user_id=member.id,
            order_by_columns=[Record.record_date],
        )
        summary_user_detail_list.append(
            SummaryUserDetail(user=member, record_list=records)
        )
        pass
    return summary_user_detail_list


async def generate_summary_detail_users_message(
    summary_user_detail_gene: list[SummaryUserDetail],
) -> str:
    summary_detail_users_message_list = []
    for summary_user_detail in summary_user_detail_gene:
        user_total_spent = user_total_income = 0
        summary_user_detail_message_list: list = []
        for record in summary_user_detail.record_list:
            if record.is_income:
                user_total_income += record.amount
                pass
            else:
                user_total_spent += record.amount
                pass
            summary_user_detail_message_list.append(
                summary_user_detail_template.format(
                    date=escape_message(record.record_date.isoformat()),
                    signed_amount = (
                        ("\+" if record.is_income else "\-")+str(record.amount)
                    ).rjust(7),
                    description=escape_message(record.description),
                )
            )
            pass
        if summary_user_detail_message_list:
            summary_user_details_message = "\n".join(summary_user_detail_message_list)
            pass
        else:
            summary_user_details_message=summary_user_detail_empty_template
            pass
        summary_user_detail_message = summary_detail_user_message_template.format(
            user_name=summary_user_detail.user.name,
            user_telegram_id=summary_user_detail.user.telegram_id,
            user_total_spent=user_total_spent,
            user_total_income=user_total_income,
            user_real_spent=escape_message(str(user_total_spent - user_total_income)),
            summary_user_details_message=summary_user_details_message,
        )
        summary_detail_users_message_list.append(summary_user_detail_message)
        pass
    summary_detail_message = "\n".join(summary_detail_users_message_list)
    return summary_detail_message


async def summary_detail_handler(message: Message, limitation_id: UUID) -> None:
    user, group = await get_user_and_group(message=message)
    limitation = await read_limitation_joined(id=limitation_id)
    summary = (await caculate_summaries(limitation_list=[limitation]))[0]
    end_date = date.today()
    if limitation.period == 0:
        start_date = end_date - timedelta(days=1)
        pass
    elif limitation.period == 1:
        start_date = end_date - timedelta(weeks=1)
        pass
    elif limitation.period == 2:
        start_date = month_manipulate(base=end_date, add_month=-1)
        pass
    elif limitation.period == 3:
        start_date = month_manipulate(base=end_date, add_month=-12)
        pass
    period_amount, period_unit = period_show_list[limitation.period].split(' ')
    period_formatted = f"{period_amount} {period_unit.rjust(5)}"
    summary_detail_message = summary_detail_message_template.format(
        period=period_formatted,
        category_name=limitation.category.name,
        amount=limitation.amount,
        total_spent=summary.total_spent,
        total_income=summary.total_income,
        total_real_spent=escape_message(str(summary.total_spent-summary.total_income)),
        start_date=escape_message(start_date.isoformat()),
        end_date=escape_message(end_date.isoformat()),
    )
    summary_user_details = await caculate_summary_details(
        group_id=group.id,
        limitation_id=limitation_id,
    )
    send_filenames = []
    for summary_user_detail in summary_user_details:
        filename = await generate_csv_file(limitation, summary_user_detail)
        filename_fields = [
            summary_user_detail.user.name,
            limitation.category.name,
            start_date.isoformat(),
            end_date.isoformat(),
        ]
        send_filename = f"./{'_'.join(filename_fields)}.csv"
        copy(filename, send_filename)
        send_filenames.append(send_filename)
        pass
    summary_detail_users_message = \
        await generate_summary_detail_users_message(
            summary_user_detail_gene=summary_user_details
        )
    final_message = summary_detail_message + summary_detail_users_message
    close_markup = InlineKeyboardMarkup(
        inline_keyboard=add_close_button([]),
    )
    await message.edit_text(
        text=final_message,
        reply_markup=close_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    for send_filename in send_filenames:
        with open(send_filename, 'rb') as f:
            await MoneybookBot().bot.send_document(
                chat_id=message.chat.id,
                document=f,
            )
            pass
        remove(send_filename)
    pass
