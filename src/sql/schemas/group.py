from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .user import ExistUser


class NewGroup(BaseModel):
    telegram_id: Optional[int] = Field(default=None)
    name: str
    admin_user_id: Optional[UUID]
    pass


class ExistGroup(NewGroup):
    id: UUID

    class Config:
        orm_mode = True
        pass
    pass


class ExtendGroup(ExistGroup):
    admin_user: ExistUser
    pass
