# balance
ask_month_message_template = "請選擇月份"
balance_reject_message = "私人對話未有此功能"
balance_message_template = """\
月份：{month} 實際總支出：{total_real_spent}
平衡：
{balance_detail_message}
"""
balance_detail_message_template = """
[{user_name}](tg://user?id={user_telegram_id}):
實出：{real_spent} 應出：{should_spent}"""
balance_detail_message_unit_template = \
    "{action} {amount} {action_prep} [{other_user_name}](tg://user?id={other_user_telegram_id})"
exclude_category_name_list = ['薪水', '領錢', '轉帳', '個人花費']
no_balance_message = "無須平衡"

# info
group_info_message_template = """\
- name: {group_name}
- telegram id: {group_telegram_id}
- members:
{member_informations}
- limitations:
{group_limitations}
"""
user_info_message_template = """\
- name: {user_name}
- telegram id: {user_telegram_id}
- joined groups:
{group_names}
"""
user_info_message_template_v2 = """\
User:
{user_name} \({user_telegram_id}\)

joined groups:
{joined_groups_info}
"""
user_joined_group_info_message_template = "{sequence}\. {group_name} \({group_telegram_id}\)"
user_joined_group_info_detail_message_template = """
  admin user: [{group_admin_user_name}](tg://user?id={group_admin_user_telegram_id})
  limitations:
{group_limitations_info_message}
"""
group_limitation_info_message_template = "    {period} {amount} {category_name}"

# limitation
limitation_created_message = "已新增預算！"
limitation_detail_message_template = """\
週期：{period}
類別：{category_name}
金額：{amount}"""
limitation_check_delete_message_template = \
limitation_detail_message_template + """

確定刪除？
"""
limitation_edit_message_template = \
limitation_detail_message_template + """

回覆此訊息新的金額
"""
limitation_page_read_message_template = "{seq}\. {period} {category_name} {amount}"
limitation_deleted_message = "已刪除預算。"
limitation_not_found_message = "無預算"
limitation_not_found_italic_message = \
    f"_{limitation_not_found_message}_"
limitation_message_template = """\
週期：{period}
類別：{category_name}
{question_text}"""
limitation_row_name_list = ['period', 'category']
limitation_undecided_text = "未選擇"
limitation_undecided_italic_text = f"_{limitation_undecided_text}_"
limitation_question_text_list = ["請選擇週期：", "請選擇類別：", "回覆此訊息金額"]

# record
record_created_message = "已新增紀錄！"
record_detail_message_template = """\
日期：{record_date}
成員：{user_name}
類型：{record_type}
類別：{category_name}
金額：{amount}
簡述：{description}"""
record_check_delete_message_template = \
record_detail_message_template + """

確定刪除？
"""
record_edit_message_template = \
record_detail_message_template + """

回覆此訊息新的金額、簡述\(選填\)，空白間隔
範例：100 晚餐
"""
record_page_read_message_template = """\
{seq}\. [{user_name}](tg://user?id={user_telegram_id}) {description}
  {record_date} {record_type} {category_name} {amount}"""
record_deleted_message = "已刪除紀錄。"
record_not_found_message = "無紀錄"
record_not_found_italic_message = f"_{record_not_found_message}_"
record_message_template = """\
日期：{record_date}
類型：{record_type}
類別：{category_name}
{question_text}"""
record_row_name_list = ['record_date', 'record_type', 'category']
record_undecided_text = "未選擇"
record_undecided_italic_text = f"_{record_undecided_text}_"
record_question_text_list = [
    "請選擇日期：",
    "收入或支出：",
    "請選擇類別：",
    "回覆此訊息金額、簡述\(選填\)，空白間隔\n範例：100 晚餐",
]

# share
permission_deny_message = "非群組管理員"
ask_member_message = "請選擇成員："
user_not_found_message = "無此用戶"
ask_share_message_template = \
    "成員：{user_name}\({user_telegram_id}\)\n回覆此訊息佔比數\(正整數\)"
share_updated_message_template = \
    "{user_name}\({user_telegram_id}\)佔比已更新為{new_share}"

# start
hello_message_template = """\
Hi [{user_name}](tg://user?id={user_telegram_id})
This group is `{group_name}`
I\'m [{bot_name}](tg://user?id={bot_telegram_id})\!
"""

# summary
no_summary_message = "查無資料"
# this should be table with sequence
summary_message_unit_template = """\
{period} {category_name} {amount}
總支出：{total_spent}
總收入：{total_income}
實際支出：{total_real_spent}
"""
summary_message_template = "{seq}\. " + summary_message_unit_template
summary_detail_message_template = summary_message_unit_template + """\
起始日期：{start_date}
結束日期：{end_date}

"""
# change this to send <group_telegram_id>_<category_id>_<period>.csv file
summary_detail_user_message_template = """\
[{user_name}](tg://user?id={user_telegram_id})
總支出：{user_total_spent}
總收入：{user_total_income}
實際支出：{user_real_spent}
{summary_user_details_message}
"""
summary_user_detail_template = "{date}  {signed_amount}  {description}"
summary_user_detail_empty_template = "_無紀錄_"