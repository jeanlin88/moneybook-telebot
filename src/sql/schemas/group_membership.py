from uuid import UUID

from pydantic import BaseModel, Field

from .group import ExistGroup
from .user import ExistUser


class NewGroupMembership(BaseModel):
    group_id: UUID
    user_id: UUID
    share: int = Field(default=1, ge=1)
    pass


class ExistGroupMembership(NewGroupMembership):
    id: UUID

    class Config:
        orm_mode = True
        pass
    pass


class ExtendGroupMembership(ExistGroupMembership):
    group: ExistGroup
    user: ExistUser
    pass
