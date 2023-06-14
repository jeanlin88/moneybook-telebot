from typing import Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Delete, Select

from ..database import get_session_maker
from ..models.user import User
from ..schemas.user import ExistUser, NewUser


async def create_user(
    new_user: NewUser, async_session_maker: sessionmaker = get_session_maker()
) -> ExistUser:
    new_orm_user = User(**new_user.dict())
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            async_session.add(new_orm_user)
            pass
        pass
    new_user = ExistUser.from_orm(new_orm_user)
    return new_user


async def read_user(
    id: UUID = None,
    telegram_id: int = None,
    async_session_maker: sessionmaker = get_session_maker(),
) -> Optional[ExistUser]:
    user: ExistUser = None
    query: Select = select(User)
    if id is not None:
        query = query.where(User.id == id)
        pass
    if telegram_id is not None:
        query = query.where(User.telegram_id == telegram_id)
        pass
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_user_list: list[ExistUser] = result.scalars().all()
    if orm_user_list:
        orm_user = orm_user_list[0]
        user = ExistUser.from_orm(orm_user)
        pass
    return user


async def read_or_create_user(user_info: NewUser) -> ExistUser:
    user = await read_user(telegram_id=user_info.telegram_id)
    if user is None:
        user = await create_user(new_user=user_info)
        pass
    return user


async def read_telegram_users(
    async_session_maker: sessionmaker = get_session_maker()
) -> list[ExistUser]:
    query: Select = select(User)
    query = query.where(User.telegram_id.is_not(None))
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_user_list: list[User] = result.scalars().all()
    user_list = [
        ExistUser.from_orm(orm_user)
        for orm_user in orm_user_list
    ]
    return user_list


async def update_user():
    pass


async def delete_user(
    user_id: UUID,
    async_session_maker: sessionmaker = get_session_maker(),
) -> None:
    query: Delete = delete(User)
    query = query.where(User.id == user_id)
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            await async_session.execute(query)
            pass
        pass
    return None
