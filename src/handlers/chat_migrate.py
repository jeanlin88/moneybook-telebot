from aiogram.types import ChatMemberUpdated, ContentTypes, Message, ChatJoinRequest
from aiogram import types
from core.aiobot import MoneybookBot
from core.logging import log
from sql.crud.group import read_or_create_group, update_group
from sql.schemas.group import ExistGroup, NewGroup
from sql.schemas.user import NewUser
from utils.tools import get_user_and_group


@MoneybookBot().dp.chat_member_handler()
async def chat_member_handler(update: ChatMemberUpdated):
    log().info("update: %s", update)

"""
@MoneybookBot().dp.my_chat_member_handler()
async def my_chat_member_handler(update: ChatMemberUpdated):
    # bot added to group
    # chat migrate => old chat member & new_chat_member (left -> join)
    log().info("update: %s", update)
"""

@MoneybookBot().dp.message_handler(content_types=ContentTypes.MIGRATE_TO_CHAT_ID)
async def chat_migrate_handler(message: Message):
    # get migrate from chat id and migrate to chat id
    old_chat_id = message.chat.id
    new_chat_id = message.migrate_to_chat_id
    user, old_group = await get_user_and_group(message=message)
    await update_group(
        update_group=ExistGroup(
            id=old_group.id,
            telegram_id=new_chat_id,
            name=old_group.name,
            admin_user_id=old_group.admin_user_id,
        )
    )
    log().info("group id change from %s to %s", old_chat_id, new_chat_id)
    """
    {
        "message_id": 228,
        "from": {
            "id": 1880329022,
            "is_bot": false,
            "first_name": "Jean",
            "last_name": "Lin",
            "language_code": "en"
        },
        "chat": {
            "id": -705523177,
            "title": "test",
            "type": "group",
            "all_members_are_administrators": false
        },
        "date": 1663815949,
        "migrate_to_chat_id": -1001749473434
    }
    """
