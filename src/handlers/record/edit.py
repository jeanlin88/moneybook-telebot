from aiogram.types import Message

from core.aiobot import MoneybookBot


@MoneybookBot().dp.message_handler(commands=['edit_record'])
async def edit_record_handler(message: Message):
    """
    list user records in this group page 1 for edition
    """
    await message.reply("此功能開發中...\n推薦先使用 /delete_record + /add_record")
    pass
