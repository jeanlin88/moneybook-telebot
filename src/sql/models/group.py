
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, BigInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine import Row

from ..database import Base
from .user import User


class Group(Base):
    __tablename__ = 'groups'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String)
    telegram_id = Column(BigInteger, unique=True)
    admin_user_id = Column(ForeignKey("users.id"))


class JoinedGroup(Row):
    Group: Group
    User: User
