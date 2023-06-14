from uuid import UUID

from pydantic import BaseModel


class NewCategory(BaseModel):
    name: str


class ExistCategory(NewCategory):
    id: UUID

    class Config:
        orm_mode = True
