from re import search
from typing import Optional

from aiogram.types import Message

from core.aiobot import MoneybookBot
from core.logging import log

from .limitation.add import bot_send_limitation
from .record.add import bot_send_record
from .share.main import handle_updating_user_share


add_record_regex = "^日期：\d{4}-\d{2}-\d{2}\n類型：(收入|支出)\n類別：.+\n回覆此訊息金額、簡述\(選填\)，空白間隔\n範例：100 晚餐$"
add_limitation_regex = "^週期：\d+ (day|week|month|year)\n類別：.+\n回覆此訊息金額$"
update_share_regex = "^成員：.+\n回覆此訊息佔比數\(正整數\)$"


@MoneybookBot().dp.message_handler(regexp='[0-9]+ ?.*')
async def int_space_description_handler(message: Message):
    log().info("message: %s", message)
    reply_to_message = message.reply_to_message
    if reply_to_message is not None and reply_to_message.from_id == MoneybookBot().bot.id:
        #log().info("\n\nrtm:\n%s\n\nm:\n%s\n\n", reply_to_message, message)
        #log().info("rtm.text: %s", reply_to_message.text)
        if search(add_record_regex, reply_to_message.text):
            await bot_send_record(record_raw=reply_to_message.text, new_data=message)
            pass
        elif search(add_limitation_regex, reply_to_message.text):
            await bot_send_limitation(limitation_raw=reply_to_message.text, new_data=message)
            pass
        elif search(update_share_regex, reply_to_message.text):
            user_detail, *_ = reply_to_message.text.split('\n')
            _, wrapped_user_telegram_id = \
                user_detail.removeprefix('成員：').removesuffix(')').split('(')
            user_telegram_id = int(wrapped_user_telegram_id)
            new_share = int(message.text)
            if new_share < 0:
                message.edit_text(text="invalid share")
                pass
            else:
                await handle_updating_user_share(
                    message=message, user_telegram_id=user_telegram_id, new_share=new_share
                )
                pass
            pass
        pass
    pass