from uuid import UUID

from pydantic import BaseModel, Field

from .category import ExistCategory


class NewLimitation(BaseModel):
    group_id: UUID
    category_id: UUID
    period: int = Field(default=0, ge=0, le=3)
    amount: int = Field(gt=0)
    pass


class ExistLimitation(NewLimitation):
    id: UUID

    class Config:
        orm_mode = True
        pass
    pass


class ExtendLimitation(ExistLimitation):
    category: ExistCategory
    pass
