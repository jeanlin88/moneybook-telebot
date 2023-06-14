from aiogram.types import Message, InlineKeyboardMarkup, ParseMode

from core.aiobot import MoneybookBot
from sql.crud.group import read_user_joined_groups
from sql.schemas.group import ExtendGroup
from sql.schemas.user import ExistUser
from utils.message_template import (
    user_info_message_template_v2,
    user_joined_group_info_message_template,
)
from utils.tools import (
    add_close_button,
    escape_message,
    get_user_and_group,
)

from .group import generate_groups_info


async def generate_info(user: ExistUser, group: ExtendGroup) -> str:
    user_joined_group_list = await read_user_joined_groups(user_id=user.id)
    user_joined_group_info_message_list = []
    for idx, user_joined_group in enumerate(user_joined_group_list):
        user_joined_groups_info_message = \
            user_joined_group_info_message_template.format(
                sequence=idx+1,
                group_name=user_joined_group.name,
                group_telegram_id=escape_message(str(user_joined_group.telegram_id)),
            )
        if user_joined_group.id == group.id:
            user_joined_group_info_detail_message = await generate_groups_info(group=group)
            user_joined_groups_info_message += user_joined_group_info_detail_message
            pass
        user_joined_group_info_message_list.append(user_joined_groups_info_message)
        pass
    user_joined_groups_info_message = \
        "\n".join(user_joined_group_info_message_list)
    user_info_message = user_info_message_template_v2.format(
        user_name=user.name,
        user_telegram_id=user.telegram_id,
        joined_groups_info=user_joined_groups_info_message,
    )
    return user_info_message


@MoneybookBot().dp.message_handler(commands=['info'])
async def info_handler(message: Message):
    """
    handle info command
    """
    user, group = await get_user_and_group(message=message)
    info = await generate_info(user=user, group=group)
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=add_close_button([])
    )
    print(info)
    await message.reply(
        text=info,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
