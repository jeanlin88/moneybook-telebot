from datetime import date

from aiogram.types.callback_query import CallbackQuery

from core.aiobot import MoneybookBot
from core.logging import log
from utils.tools import (
    SPACE,
    get_category_dict,
    is_action_with_id,
    is_date,
    is_uuid,
    move_base_date,
    move_base_month,
    period_show_list,
)

from .balance import send_balance_message
from .limitation.add import handle_limitation_callback
from .limitation.delete import bot_delete_limitation, handle_delete_limitation_callback
from .limitation.read import handle_read_limitation_callback
from .record.delete import bot_delete_record, handle_delete_record_callback
from .record.read import handle_download_csv_callback, handle_read_record_callback
from .record.add import handle_record_callback
from .record.base import record_message_pagination
from .share import handle_share_asking
from .summary import summary_detail_handler


@MoneybookBot().dp.callback_query_handler()
async def callback_handler(callback_query: CallbackQuery) -> None:
    from_user = callback_query.from_user
    message = callback_query.message
    if message.from_user != from_user:
        message.from_user = from_user
        pass
    data = callback_query.data
    if not data:
        return None
    await callback_query.answer(text=data, cache_time=30)
    if data in ["close", "cancel"]:
        await message.edit_text(text=f"{data}.")
        return None
    # will be None if message not replying any another message
    reply_to_message = message.reply_to_message
    log().info("\nmessage: %s\ndata: %s\nreply_to_message: %s\n", message, data, reply_to_message)
    if reply_to_message is not None:
        # /info, /add_record, etc.
        bot_command = callback_query.message.reply_to_message.text
        if f"@{MoneybookBot().name}" in bot_command:
            bot_command = bot_command.removesuffix(f"@{MoneybookBot().name}")
            pass
        log().info("bot_command: %s", bot_command)
        if bot_command == "/add_limitation":
            # data format:
            # 1. period chosen: 1 day | 1 week | 1 month | 1 year
            # 2. category chosen: category_name
            if (
                data in period_show_list or
                data in await get_category_dict()
            ):
                await handle_limitation_callback(message=message, new_data=data)
                pass
            else:
                log().error("Unexpected data: %s", data)
                pass
            pass
        elif bot_command == "/add_record":
            # data format:
            # 1. moving base date: next | prev
            # 2. date chosen: date
            # 3. type chosen: 收入 | 支出
            # 4. category chosen: category_name
            if data in ['next', 'prev']:
                inline_keyboard = message.reply_markup.inline_keyboard
                current_base_date = inline_keyboard[0][3].callback_data
                move = 1 if data == 'next' else -1
                await move_base_date(
                    move=move,
                    base_date_str=current_base_date,
                    message=message,
                )
                pass
            elif (
                is_date(data) or
                data in ['收入', '支出'] or
                data in await get_category_dict()
            ):
                await handle_record_callback(message=message, new_data=data)
                pass
            else:
                log().error("Unexpected data: %s", data)
                pass
            pass
        elif bot_command == "/balance":
            # data format:
            # 1. moving base month: next | prev
            # 2. month chosen: month
            if data in ['next', 'prev']:
                inline_keyboard = message.reply_markup.inline_keyboard
                current_base_month = inline_keyboard[0][3].callback_data
                move = 1 if data == 'next' else -1
                await move_base_month(
                    move=move,
                    base_month_str=current_base_month,
                    message=message,
                )
                pass
            elif is_date(data):
                base_month = date.fromisoformat(data)
                await send_balance_message(message=message, base_month=base_month, reply=False)
                pass
            else:
                log().error("Unexpected data: %s", data)
                pass
            pass
        elif bot_command == "/delete_limitation":
            # data format:
            # 1. limitation chosen: limitation_id
            # 2. double check chosen: sure | cancel
            if is_uuid(data):
                await handle_delete_limitation_callback(
                    message=message,
                    limitation_id=data,
                )
                pass
            elif is_action_with_id(data):
                action, id = data.split(SPACE)
                await bot_delete_limitation(message=message, limitation_id=id)
                pass
            else:
                log().error("Unexpected data: %s", data)
                pass
            pass
        elif bot_command == "/delete_record":
            # data format:
            # 1. moving page: new_page
            # 2. record chosen: record_id
            # 3. double check chosen: sure | cancel
            if data.isdigit():
                await record_message_pagination(
                    message=message,
                    pagination_type='delete',
                    new_page=int(data),
                    reply=False,
                )
            elif is_uuid(data):
                await handle_delete_record_callback(
                    message=message,
                    record_id=data,
                )
                pass
            elif is_action_with_id(data):
                action, id = data.split(SPACE)
                await bot_delete_record(message=message, record_id=id)
                pass
            else:
                log().error("Unexpected data: %s", data)
                pass
            pass
        elif bot_command == "/edit_limitation":
            # data format:
            # 1. limitation chosen: limitation_id
            if is_uuid(data):
                log().info("limitation %s selected. show detail then ask amount.", data)
                pass
            else:
                log().error("Unexpected data: %s", data)
                pass
            pass
        elif bot_command == "/edit_record":
            # data format:
            # 1. moving page: new_page
            # 2. record chosen: record_id
            if data.isdigit():
                log().info("move to page %s", data)
            elif is_uuid(data):
                log().info("record %s selected. show detail then ask amount and description.", data)
                pass
            else:
                log().error("Unexpected data: %s", data)
                pass
            pass
        elif bot_command == "/read_limitation":
            # data format:
            # 1. limitation chosen: limitation_id
            if is_uuid(data):
                await handle_read_limitation_callback(message=message, limitation_id=data)
                pass
            else:
                log().error("Unexpected data: %s", data)
                pass
            pass
        elif bot_command == "/read_record":
            # data format:
            # 1. moving page: new_page
            # 2. record chosen: record_id
            if data.isdigit():
                await record_message_pagination(
                    message=message,
                    pagination_type='read',
                    new_page=int(data),
                    reply=False,
                )
            elif is_uuid(data):
                await handle_read_record_callback(message=message, record_id=data)
                pass
            elif data == 'csv':
                await handle_download_csv_callback(message=message)
                pass
            else:
                log().error("Unexpected data: %s", data)
                pass
            pass
        elif bot_command == "/share":
            # data format:
            # 1. user chosen: user_telegram_id
            if data.isdigit():
                await handle_share_asking(message=message, user_telegram_id=int(data))
                pass
            else:
                log().error("Unexpected data: %s", data)
                pass
            pass
        elif bot_command == "/summary":
            # data format:
            # 1. limitation chosen: limitation_id
            if is_uuid(data):
                await summary_detail_handler(message=message, limitation_id=data)
                pass
            else:
                log().error("Unexpected data: %s", data)
                pass
            pass
        pass
    pass
