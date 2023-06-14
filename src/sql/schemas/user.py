from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class NewUser(BaseModel):
    telegram_id: Optional[int] = Field(default=None, gt=0)
    name: str
    pass


class ExistUser(NewUser):
    id: UUID

    class Config:
        orm_mode = True
        pass
    pass
