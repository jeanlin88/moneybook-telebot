from aiogram.types import Message

from core.aiobot import MoneybookBot


@MoneybookBot().dp.message_handler(commands=['edit_limitation'])
async def edit_limitation_handler(message: Message):
    """
    list limitation in this group for edition
    """
    await message.reply("此功能開發中...\n推薦先使用 /delete_limitation + /add_limitation")
    pass
