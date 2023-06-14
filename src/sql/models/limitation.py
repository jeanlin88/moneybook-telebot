
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine import Row

from ..database import Base
from .category import Category
from .group import Group


class Limitation(Base):
    __tablename__ = 'limitations'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    category_id = Column(ForeignKey("categories.id"))
    group_id = Column(ForeignKey("groups.id"))
    period = Column(Integer)
    amount = Column(Integer)


class JoinedLimitation(Row):
    Category: Category
    Group: Group
    Limitation: Limitation
