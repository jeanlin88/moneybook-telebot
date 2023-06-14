from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from .category import ExistCategory
from .group import ExistGroup
from .limitation import ExistLimitation, ExtendLimitation
from .user import ExistUser


class NewRecord(BaseModel):
    record_date: date
    user_id: UUID
    group_id: UUID
    category_id: UUID
    is_income: bool
    amount: int = Field(gt=0)
    description: str = Field(default='')
    pass


class ExistRecord(NewRecord):
    id: UUID

    class Config:
        orm_mode = True
        pass
    pass


class ExtendRecord(ExistRecord):
    user: ExistUser
    group: ExistGroup
    category: ExistCategory
    pass


class SpentDetail(BaseModel):
    diff: int = Field(default=0)
    real_spent: int = Field(default=0)
    should_spent: int = Field(default=0)
    order: float
    pass


class UserSumup(BaseModel):
    user: ExistUser
    detail: SpentDetail
    pass


class SummaryUserDetail(BaseModel):
    user: ExistUser
    record_list: list[ExtendRecord]
    pass


class Summary(BaseModel):
    limitation: ExtendLimitation
    total_spent: int
    total_income: int
    pass
