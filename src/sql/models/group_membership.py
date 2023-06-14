
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine import Row

from .group import Group
from .user import User
from ..database import Base


class GroupMembership(Base):
    __tablename__ = 'group_memberships'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(ForeignKey("users.id"))
    group_id = Column(ForeignKey("groups.id"))
    share = Column(Integer, default=1)


class JoinedGroupMembership(Row):
    GroupMembership: GroupMembership
    Group: Group
    User: User
