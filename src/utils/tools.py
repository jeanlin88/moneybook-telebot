from datetime import date, datetime, timedelta
from typing import Literal, Optional, Union
from uuid import UUID

from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from core.aiobot import MoneybookBot
from sql.crud.category import read_categories
from sql.crud.group import read_or_create_group
from sql.crud.group_membership import create_group_memberships, read_group_memberships
from sql.crud.user import read_or_create_user
from sql.schemas.category import ExistCategory
from sql.schemas.group import ExistGroup, ExtendGroup, NewGroup
from sql.schemas.group_membership import NewGroupMembership
from sql.schemas.limitation import ExistLimitation, ExtendLimitation
from sql.schemas.user import ExistUser, NewUser


SPACE = " "
period_show_list = ['1 day', '1 week', '1 month', '1 year']


def add_close_button(
    inline_keyboard: Optional[list[list[InlineKeyboardButton]]],
) -> list[list[InlineKeyboardButton]]:
    if inline_keyboard is not None:
        close_button = InlineKeyboardButton(text="close", callback_data="close")
        inline_keyboard.append([close_button])
        pass
    return inline_keyboard


def caculate_start_date_by_period(period: int) -> date:
    today = date.today()
    if period == 0:
        return today - timedelta(days=7)
    elif period == 1:
        return today - timedelta(weeks=1)
    elif period == 2:
        return month_manipulate(base=today, add_month=-1)
    elif period == 3:
        return month_manipulate(base=today, add_month=-12)
    pass


def count_chinese(message: str) -> int:
    chinese_counter = 0
    for char in message:
        if '\u4e00' <= char <= '\u9fff':
            chinese_counter += 1
    return chinese_counter


def month_manipulate(
        base: Union[date, datetime],
        add_month: int,
        days: Literal['first', 'current', 'last'] = 'current') -> Union[date, datetime]:
    if base.month + add_month > 12:
        add_year = (base.month + add_month) // 12
        new_month = (base.month + add_month) % 12
        new_year = base.year + add_year
        pass
    elif base.month + add_month < 0:
        add_year = (base.month + add_month) // 12
        new_year = base.year + add_year
        new_month = (base.month + add_month) - add_year * (12)
        pass
    elif base.month + add_month == 0:
        new_year = base.year - 1
        new_month = 12
    else:
        new_year = base.year
        new_month = base.month + add_month
        pass

    if days == 'first':
        new_day = 1
        pass
    elif days == 'last':
        new_day = 31
        while True:
            try:
                d = date(new_year, new_month, new_day)
                break
            except Exception as ex:
                new_day -= 1
                pass
            pass
    else:
        new_day = base.day
        pass

    added = base.replace(year=new_year, month=new_month, day=new_day)
    return added


def extend_chinese(message: str, max: int) -> str:
    chinese_count = count_chinese(message=message)
    if len(message) + chinese_count > max:
        idx = max - 3
        for char in message[:max-3]:
            if count_chinese(char):
                idx -= 1
        msg = message[:idx] + '...'
        return msg
    else:
        msg = message.rjust(max-chinese_count)
    return msg


async def ensure_user_in_group(user_id: UUID, group: ExistGroup) -> None:
    group_membership = await read_group_memberships(
        group_id=group.id,
        user_id=user_id,
    )
    if not group_membership:
        await create_group_memberships(
            new_group_memberships=[
                NewGroupMembership(user_id=user_id, group_id=group.id)
            ]
        )
        pass
    return None


def escape_message(message: str, html: bool = False) -> str:
    escape_chars = "_*[]()~`>#+-=|{}.!"
    replace_dict = {
        '<': '&lt;',
        '>': '&gt;',
        '&': '&amp;',
    }
    if html:
        for char in replace_dict:
            message = message.replace(char, replace_dict[char])
            pass
        pass
    else:
        for char in escape_chars:
            message = message.replace(char, f"\{char}")
            pass
        pass
    return message


async def extend_group_limitation_list(
        limitation_list: list[ExistLimitation]) -> list[ExtendLimitation]:
    category_dict = await get_category_dict()
    extend_limitation_list = [
        ExtendLimitation(
            **limitation.dict(),
            category=category_dict[limitation.category_id])
        for limitation in limitation_list
    ]
    return extend_limitation_list


def generate_check_delete_buttons(id: str) -> list[InlineKeyboardButton]:
    """
    generate ok and cancel button
    """
    check_delete_button_list = [
        InlineKeyboardButton(text="sure", callback_data=f"delete {id}"),
        InlineKeyboardButton(text="cancel", callback_data="cancel"),
    ]
    return check_delete_button_list


def generate_date_button_list(base_date: datetime) -> list[InlineKeyboardButton]:
    """
    generate date button list:
    1. prev base date
    2. base date - 2d
    3. base date - 1d
    4. base date
    5. next base date
    """
    date_list = [base_date + timedelta(days=i) for i in range(-2, 1)]
    prev_button = InlineKeyboardButton(text='<', callback_data='prev')
    next_button = InlineKeyboardButton(text='>', callback_data='next')
    date_buttons = [
        InlineKeyboardButton(
            text=date_element.strftime("%m-%d"),
            callback_data=date_element.isoformat()[:10],
        )
        for date_element in date_list
    ]
    date_button_list = [prev_button, *date_buttons, next_button]
    return date_button_list


def generate_month_button_list(base_month: datetime) -> list[InlineKeyboardButton]:
    """
    generate month button list:
    x1. prev base month
    2. base month - 2m
    3. base month - 1m
    4. base month
    x5. next base month
    """
    month_list = [
        month_manipulate(base_month, add_month=i)
        for i in range(-2, 1)
    ]
    prev_button = InlineKeyboardButton(text='<', callback_data='prev')
    next_button = InlineKeyboardButton(text='>', callback_data='next')
    month_buttons = [
        InlineKeyboardButton(
            text=month_element.strftime("%Y-%m"),
            callback_data=month_element.strftime("%Y-%m-%d"),
        )
        for month_element in month_list
    ]
    #month_button_list = [prev_button, *month_buttons, next_button]
    month_button_list = month_buttons
    return month_button_list


def generate_page_button_list(base_page: int = 1) -> list[InlineKeyboardButton]:
    if base_page <= 2:
        m2_page = m1_page = 1
        pass
    elif base_page == 3:
        m2_page = 1
        m1_page = 2
        pass
    else:
        m2_page = base_page - 2
        m1_page = base_page - 1
        pass

    page_button_list = [
        InlineKeyboardButton(text="<<", callback_data=str(m2_page)),
        InlineKeyboardButton(text="<", callback_data=str(m1_page)),
        InlineKeyboardButton(text=str(base_page), callback_data=str(base_page)),
        InlineKeyboardButton(text=">", callback_data=str(base_page + 1)),
        InlineKeyboardButton(text=">>", callback_data=str(base_page + 2)),
    ]
    return page_button_list


def generate_period_buttons_list() -> list[list[InlineKeyboardButton]]:
    """
    generate period selection buttons
    """
    period_button_list = []
    for period in period_show_list:
        button = InlineKeyboardButton(text=period, callback_data=period)
        if not period_button_list:
            period_button_list = [[button]]
            pass
        elif len(period_button_list[-1]) == 5:
            period_button_list.append([button])
            pass
        else:
            period_button_list[-1].append(button)
            pass
        pass
    return period_button_list


def generate_seq_buttons_list(
    id_list: list[UUID],
    base: int,
) -> list[InlineKeyboardButton]:
    seq_button_list = [
        InlineKeyboardButton(
            text=str(base+idx+1),
            callback_data=str(id_list[idx]),
        )
        for idx in range(len(id_list))
    ]
    return seq_button_list


async def get_category_dict() -> dict[Union[UUID, str], ExistCategory]:
    categories = await read_categories()
    category_dict = {}
    for category in categories:
        category_dict[category.id] = category
        category_dict[category.name] = category
    return category_dict


async def get_user_and_group(message: Message) -> tuple[ExistUser, ExtendGroup]:
    chat = message.chat
    from_user = message.from_user
    if from_user.id == MoneybookBot().bot.id:
        from_user = message.reply_to_message.from_user
        pass
    user_info = NewUser(telegram_id=from_user.id, name=from_user.full_name)
    user = await read_or_create_user(user_info=user_info)
    group_info = NewGroup(
        telegram_id=chat.id,
        name=chat.full_name,
        admin_user_id=user.id,
    )
    group = await read_or_create_group(group_info=group_info)
    if getattr(group, "admin_user", None) is None:
        group = ExtendGroup(**group.dict(), admin_user=user)
        pass
    return (user, group)


def is_action_with_id(target: str) -> bool:
    if target.count(SPACE) != 1:
        return False
    action, id = target.split(SPACE)
    if action in ['delete'] and is_uuid(id):
        return True
    else:
        return False


def is_date(target: str) -> bool:
    try:
        trans_date = date.fromisoformat(target)
        return True
    except ValueError as VE:
        return False


def is_uuid(target: str) -> bool:
    try:
        id = UUID(target)
        return True
    except ValueError as VE:
        return False


async def move_base_date(
    move: int, base_date_str: str, message: Message,
) -> None:
    base_date = datetime.fromisoformat(base_date_str)
    new_base_date = base_date + timedelta(days=move)
    new_inline_keyboard = [generate_date_button_list(base_date=new_base_date)]
    new_reply_markup = InlineKeyboardMarkup(
        inline_keyboard=add_close_button(new_inline_keyboard)
    )
    await message.edit_reply_markup(reply_markup=new_reply_markup)


async def move_base_month(
    move: int, base_month_str: str, message: Message,
) -> None:
    base_month = datetime.fromisoformat(base_month_str)
    new_base_month = month_manipulate(base_month, add_month=move)
    new_inline_keyboard = [generate_month_button_list(base_month=new_base_month)]
    new_reply_markup = InlineKeyboardMarkup(
        inline_keyboard=add_close_button(new_inline_keyboard)
    )
    await message.edit_reply_markup(reply_markup=new_reply_markup)