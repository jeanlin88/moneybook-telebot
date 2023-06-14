from datetime import date

from aiogram.types import Message, InlineKeyboardMarkup, ParseMode

from core.aiobot import MoneybookBot
from utils.message_template import (
    ask_month_message_template,
    balance_message_template,
    balance_reject_message,
)
from utils.tools import (
    add_close_button,
    escape_message,
    generate_month_button_list,
    get_user_and_group,
    month_manipulate,
)

from .caculator import caculate_balance
from .message_generator import generate_balance_details_message


async def send_balance_message(message: Message, base_month: date, reply: bool = False) -> None:
    """
    send balance message to chat
    reject if is private chat
    """
    _, group = await get_user_and_group(message=message)
    balance_list = await caculate_balance(group=group, month=base_month)
    balance_details_message = generate_balance_details_message(balance_list)
    total_real_spent = sum([
        user_sumup.detail.real_spent for user_sumup in balance_list
    ])
    balance_message = balance_message_template.format(
        month=base_month.strftime("%Y\-%m"),
        total_real_spent=escape_message(str(total_real_spent)),
        balance_detail_message=balance_details_message,
    )
    close_markup = InlineKeyboardMarkup(
        inline_keyboard=add_close_button([]),
    )
    if reply:
        await message.reply(
            text=balance_message,
            reply_markup=close_markup,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        pass
    else:
        print(balance_message)
        await message.edit_text(
            text=balance_message,
            reply_markup=close_markup,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        pass
    pass


@MoneybookBot().dp.message_handler(commands=['balance'])
async def balance_handler(message: Message):
    user, group = await get_user_and_group(message=message)
    if user.telegram_id == group.telegram_id:
        await message.reply(text=balance_reject_message)
        return None

    inline_keyboard = [
        generate_month_button_list(
            base_month=date.today().replace(day=1)
        )
    ]
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=add_close_button(inline_keyboard)
    )
    await message.reply(
        text=ask_month_message_template,
        reply_markup=reply_markup,
    )
    pass


@MoneybookBot().dp.message_handler(commands=['fast_balance'])
async def fast_balance_handler(message: Message):
    user, group = await get_user_and_group(message=message)
    if user.telegram_id == group.telegram_id:
        await message.reply(text=balance_reject_message)
        return None

    last_month = month_manipulate(
        base=date.today(),
        add_month=-1,
        days='first',
    )
    await send_balance_message(message=message, base_month=last_month, reply=True)
    await send_balance_message(message=message, base_month=date.today(), reply=True)
    pass
