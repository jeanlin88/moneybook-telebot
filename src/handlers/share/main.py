from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from core.aiobot import MoneybookBot

from sql.crud.group_membership import (
    read_group_memberships,
    read_group_memberships_joined,
    update_group_membership,
)
from sql.crud.user import read_user
from utils.tools import add_close_button, get_user_and_group
from utils.message_template import (
    ask_member_message,
    ask_share_message_template,
    share_updated_message_template,
    permission_deny_message,
    user_not_found_message,
)


async def handle_updating_user_share(
    message: Message, user_telegram_id: int, new_share: int
) -> None:
    user, group = await get_user_and_group(message=message)
    if group.admin_user_id != user.id:
        await message.edit_text(text=permission_deny_message)
        pass
    else:
        change_user = await read_user(telegram_id=user_telegram_id)
        if change_user is None:
            await message.edit_text(text=user_not_found_message)
            pass
        else:
            group_membership = (await read_group_memberships(
                group_id=group.id, user_id=change_user.id
            ))[0]
            group_membership.share = new_share
            await update_group_membership(group_membership)
            share_updated_message = share_updated_message_template.format(
                user_name=change_user.name,
                user_telegram_id=change_user.telegram_id,
                new_share=new_share,
            )
            await MoneybookBot().bot.send_message(
                chat_id=group.telegram_id,
                text=share_updated_message,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            pass
        pass
    pass


async def handle_share_asking(message: Message, user_telegram_id: int) -> None:
    user, group = await get_user_and_group(message=message)
    if group.admin_user_id != user.id:
        await message.edit_text(text=permission_deny_message)
        pass
    else:
        change_user = await read_user(telegram_id=user_telegram_id)
        if change_user is None:
            await message.edit_text(text=user_not_found_message)
            pass
        else:
            ask_share_message = ask_share_message_template.format(
                user_name=change_user.name,
                user_telegram_id=change_user.telegram_id,
            )
            close_markup = InlineKeyboardMarkup(
                inline_keyboard=add_close_button([]),
            )
            await message.edit_text(
                text=ask_share_message,
                reply_markup=close_markup,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            pass
        pass
    pass


@MoneybookBot().dp.message_handler(commands=['share'])
async def share_handler(message: Message):
    user, group = await get_user_and_group(message=message)
    if group.admin_user_id != user.id:
        await message.reply(text=permission_deny_message)
        pass
    else:
        group_membership_list = await read_group_memberships_joined(group_id=group.id)
        group_member_list = [
            group_membership.user
            for group_membership in group_membership_list
        ]
        inline_keyboard = [
            [
                InlineKeyboardButton(
                    text=f"{member.name}({member.telegram_id})",
                    callback_data=str(member.telegram_id),
                )
                for member in group_member_list[idx:idx+5]
            ]
            for idx in range(0, len(group_member_list), 5)
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        await message.reply(
            text=ask_member_message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        pass
