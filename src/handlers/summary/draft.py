from datetime import date
from sql.crud.record import read_records
from sql.schemas.limitation import ExistLimitation, ExtendLimitation
from sql.schemas.record import Summary
from utils.tools import caculate_start_date_by_period, escape_message, get_category_dict, period_show_list
from utils.message_template import summary_message_template, no_summary_message


async def caculate_summaries(limitation_list: list[ExtendLimitation]) -> list[Summary]:
    summary_list = []
    for limitation in limitation_list:
        before_date = date.today()
        after_date = caculate_start_date_by_period(period=limitation.period)
        records = await read_records(
            category_ids=[limitation.category_id],
            group_id=limitation.group_id,
            date_before=before_date,
            date_after=after_date,
        )
        total_spent = total_income = 0
        for record in records:
            if record.is_income:
                total_income += record.amount
                pass
            else:
                total_spent += record.amount
                pass
            pass
        summary = Summary(
            limitation=limitation,
            total_spent=total_spent,
            total_income=total_income,
        )
        summary_list.append(summary)
        pass
    return summary_list


async def generate_summary_message(summary_list: list[Summary]) -> str:
    summary_message_list = []
    for idx, summary in enumerate(summary_list):
        period_amount, period_unit = period_show_list[summary.limitation.period].split(' ')
        period_formatted = f"{period_amount} {period_unit.rjust(5)}"
        summary_message = summary_message_template.format(
            seq=idx+1,
            period=period_formatted,
            category_name=summary.limitation.category.name,
            amount=summary.limitation.amount,
            total_spent=summary.total_spent,
            total_income=summary.total_income,
            total_real_spent=escape_message(str(summary.total_spent-summary.total_income)),
        )
        summary_message_list.append(summary_message)
        pass
    summaries_message = "\n".join(summary_message_list)
    if summaries_message:
        return summaries_message
    else:
        return no_summary_message
