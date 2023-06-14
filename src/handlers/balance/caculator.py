from collections import defaultdict
from datetime import date
from math import floor

from sql.crud.category import read_categories
from sql.crud.group_membership import read_group_memberships_joined
from sql.crud.record import read_records_joined
from sql.schemas.group import ExistGroup
from sql.schemas.record import ExtendRecord, SpentDetail, UserSumup
from utils.message_template import exclude_category_name_list
from utils.tools import month_manipulate


async def caculate_balance(group: ExistGroup, month: date) -> list[UserSumup]:
    """
    get member spent detail from db
    order by (UserSumup.should_spent - UserSumup.real_spent) desc
    """
    exclude_category_list = [
        category.id
        for category in await read_categories(category_name_list=exclude_category_name_list)
    ]
    group_membership_list = await read_group_memberships_joined(group_id=group.id)
    total_share = sum([
        group_membership.share for group_membership in group_membership_list
    ])
    after_date = month_manipulate(base=month, add_month=0, days='first')
    before_date = month_manipulate(base=month, add_month=0, days='last')

    member_spent_dict = defaultdict(int)
    member_income_dict = defaultdict(int)
    records: list[ExtendRecord] = await read_records_joined(
        category_ids=exclude_category_list,
        category_reverse=True,
        date_after=after_date,
        date_before=before_date,
        group_id=group.id,
    )
    total_spent = total_income = 0
    for record in records:
        if record.is_income:
            member_income_dict[record.user_id] += record.amount
            total_income += record.amount
            pass
        else:
            member_spent_dict[record.user_id] += record.amount
            total_spent += record.amount
            pass
        pass
    member_balance_list: list[UserSumup] = []
    total_real_spent = total_spent - total_income
    total_should_spent = 0

    for group_membership in group_membership_list:
        group_member = group_membership.user
        income = member_income_dict[group_member.id]
        spent = member_spent_dict[group_member.id]
        #實際支出 = 支出-收入
        real_spent = spent - income
        #應該支出 = 實際總支出 * 此成員份數 / 總份數
        should_spent = total_real_spent * group_membership.share / total_share
        # 少出的
        order = should_spent - floor(should_spent)
        # 應該支出轉為整數
        should_spent = floor(should_spent)
        user_sumup = UserSumup(
            user=group_member,
            detail=SpentDetail(
                diff=real_spent-should_spent,
                real_spent=real_spent,
                should_spent=should_spent,
                order=order,
            ),
        )
        member_balance_list.append(user_sumup)
        total_should_spent += should_spent
        pass

    # 總共少付的
    missing = total_real_spent - total_should_spent
    member_balance_list.sort(key=lambda x: x.detail.order, reverse=True)
    member_count = len(member_balance_list)
    total_add_spent = 0
    for idx, member_balance in enumerate(member_balance_list):
        add_spent = (missing // member_count)
        if missing % member_count >= idx + 1:
            add_spent += 1
            pass
        member_balance.detail.should_spent += add_spent
        member_balance.detail.diff -= add_spent
        total_add_spent += add_spent
        pass
    assert total_add_spent == missing
    member_balance_list.sort(key=lambda x: x.detail.diff)

    return member_balance_list
