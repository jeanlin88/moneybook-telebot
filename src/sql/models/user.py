from uuid import uuid4

from sqlalchemy import Column, BigInteger, String
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String)
    telegram_id = Column(BigInteger, unique=True)
