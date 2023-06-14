from sql.crud.limitation import read_limitations_joined
from sql.schemas.group import ExtendGroup
from sql.schemas.limitation import ExtendLimitation
from utils.message_template import (
    limitation_not_found_italic_message,
    user_joined_group_info_detail_message_template,
    group_limitation_info_message_template,
)
from utils.tools import (
    SPACE,
    period_show_list,
)


async def generate_groups_info(group: ExtendGroup) -> str:
    group_limitation_list: list[ExtendLimitation] = await read_limitations_joined(group_id=group.id)
    group_limitation_info_list = []
    for group_limitation in group_limitation_list:
        limitation_period_str = period_show_list[group_limitation.period]
        limitation_period_formatted_str = \
            limitation_period_str[0] + limitation_period_str[1:].rjust(6)
        group_limitation_info_list.append(
            group_limitation_info_message_template.format(
                period=limitation_period_formatted_str,
                amount=group_limitation.amount,
                category_name=group_limitation.category.name,
            )
        )
        pass
    if group_limitation_info_list:
        group_limitation_info_message = "\n".join(group_limitation_info_list)
        pass
    else:
        group_limitation_info_message = SPACE * 4 + limitation_not_found_italic_message
    group_info_detail_message = \
        user_joined_group_info_detail_message_template.format(
            group_telegram_id=group.telegram_id,
            group_admin_user_name=group.admin_user.name,
            group_admin_user_telegram_id=group.admin_user.telegram_id,
            group_limitations_info_message=group_limitation_info_message,
        )
    return group_info_detail_message
