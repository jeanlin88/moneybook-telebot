from datetime import date
from uuid import uuid4

from sqlalchemy import (
    Boolean, Column, Date, ForeignKey, Integer, String
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine import Row

from ..database import Base
from .category import Category
from .group import Group
from .user import User


class Record(Base):
    __tablename__ = 'records'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    category_id = Column(ForeignKey("categories.id"))
    group_id = Column(ForeignKey("groups.id"))
    user_id = Column(ForeignKey("users.id"))
    record_date = Column(Date, default=date.today())
    is_income = Column(Boolean)
    amount = Column(Integer)
    description = Column(String)


class JoinedRecord(Row):
    Category: Category
    Group: Group
    Record: Record
    User: User
