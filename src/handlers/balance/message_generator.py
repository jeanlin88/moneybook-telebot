from uuid import UUID

from sql.schemas.record import UserSumup
from utils.message_template import (
    balance_detail_message_template,
    balance_detail_message_unit_template,
    no_balance_message,
)


def generate_balance_details_message(balance_list: list[UserSumup]) -> str:
    from_idx = 0
    to_idx = len(balance_list) - 1
    balance_detail_message_list_dict: dict[UUID, list[str]] = {}
    while from_idx < to_idx:
        from_user_sumup = balance_list[from_idx]
        to_user_sumup = balance_list[to_idx]

        if from_user_sumup.detail.diff == 0:
            from_idx += 1
            pass
        if to_user_sumup.detail.diff == 0:
            to_idx -= 1
            pass
        if not from_user_sumup.detail.diff or not to_user_sumup.detail.diff:
            continue

        after_pay = from_user_sumup.detail.diff + to_user_sumup.detail.diff
        if after_pay > 0:
            to_idx -= 1
            pass
        else:
            from_idx += 1
            pass

        to_balance_detail_message_unit = balance_detail_message_unit_template.format(
            action="get",
            amount=to_user_sumup.detail.diff,
            action_prep="from",
            other_user_name=from_user_sumup.user.name,
            other_user_telegram_id=from_user_sumup.user.telegram_id,
        )
        if to_user_sumup.user.id not in balance_detail_message_list_dict:
            balance_detail_message = balance_detail_message_template.format(
                user_name=to_user_sumup.user.name,
                user_telegram_id=to_user_sumup.user.telegram_id,
                real_spent=to_user_sumup.detail.real_spent,
                should_spent=to_user_sumup.detail.should_spent,
            )
            balance_detail_message_list_dict[to_user_sumup.user.id] = [balance_detail_message]
            pass
        balance_detail_message_list_dict[to_user_sumup.user.id].append(to_balance_detail_message_unit)

        from_balance_detail_message_unit = balance_detail_message_unit_template.format(
            action="pay",
            amount=-from_user_sumup.detail.diff,
            action_prep="to",
            other_user_name=to_user_sumup.user.name,
            other_user_telegram_id=to_user_sumup.user.telegram_id,
        )
        if from_user_sumup.user.id not in balance_detail_message_list_dict:
            balance_detail_message = balance_detail_message_template.format(
                user_name=from_user_sumup.user.name,
                user_telegram_id=from_user_sumup.user.telegram_id,
                real_spent=from_user_sumup.detail.real_spent,
                should_spent=from_user_sumup.detail.should_spent,
            )
            balance_detail_message_list_dict[from_user_sumup.user.id] = [balance_detail_message]
            pass
        balance_detail_message_list_dict[from_user_sumup.user.id].append(from_balance_detail_message_unit)

        if after_pay > 0:
            from_user_sumup.detail.diff = after_pay
            pass
        else:
            to_user_sumup.detail.diff = after_pay
            pass
        pass

    balance_detail_messages = "\n".join([
        "\n".join(balance_detail_message_list_dict[user_id])
        for user_id in balance_detail_message_list_dict
    ])
    if not balance_detail_messages:
        balance_detail_messages = no_balance_message
        pass
    return balance_detail_messages
