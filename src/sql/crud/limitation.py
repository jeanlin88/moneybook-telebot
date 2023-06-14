from typing import Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import Select, Delete

from ..database import get_session_maker
from ..models.category import Category
from ..models.group import Group
from ..models.limitation import JoinedLimitation, Limitation
from ..schemas.category import ExistCategory
from ..schemas.group import ExistGroup
from ..schemas.limitation import ExistLimitation, NewLimitation, ExtendLimitation


async def create_limitation(
    new_limitation: NewLimitation,
    async_session_maker: sessionmaker = get_session_maker()
) -> ExistLimitation:
    new_orm_limitation = Limitation(**new_limitation.dict())
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            async_session.add(new_orm_limitation)
            pass
        pass
    new_limitation = ExistLimitation.from_orm(new_orm_limitation)
    return new_limitation


async def read_limitation(
    limitation_id: UUID, async_session_maker: sessionmaker = get_session_maker()
) -> Optional[ExistLimitation]:
    limitation: ExistLimitation = None
    query: Select = select(Limitation)
    query = query.where(Limitation.id == limitation_id)
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_limitationq_list: list[Limitation] = result.scalars().all()
    if orm_limitationq_list:
        orm_limitation = orm_limitationq_list[0]
        limitation = ExistLimitation.from_orm(orm_limitation)
        pass
    return limitation


async def read_limitation_joined(
    id: UUID, async_session_maker: sessionmaker = get_session_maker()
) -> Optional[ExtendLimitation]:
    extend_limitation: ExtendLimitation = None
    query: Select = select(Limitation, Category, Group)
    query = query.join_from(Limitation, Category,
                            Limitation.category_id == Category.id)
    query = query.join_from(Limitation, Group, Limitation.group_id == Group.id)
    if id is not None:
        query = query.where(Limitation.id == id)
        pass
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
    orm_extend_limitation_list: list[JoinedLimitation] = result.fetchall()
    if orm_extend_limitation_list:
        orm_extend_limitation = orm_extend_limitation_list[0]
        extend_limitation = ExtendLimitation(
            **ExistLimitation.from_orm(orm_extend_limitation.Limitation).dict(),
            category=ExistCategory.from_orm(orm_extend_limitation.Category),
            group=ExistGroup.from_orm(orm_extend_limitation.Group),
        )
        pass
    return extend_limitation


async def read_limitations(
    category_id: Optional[UUID] = None,
    group_id: Optional[UUID] = None,
    period: Optional[UUID] = None,
    async_session_maker: sessionmaker = get_session_maker(),
) -> list[ExistLimitation]:
    query: Select = select(Limitation)
    if category_id is not None:
        query = query.where(Limitation.category_id == category_id)
        pass
    if group_id is not None:
        query = query.where(Limitation.group_id == group_id)
        pass
    if period is not None:
        query = query.where(Limitation.period == period)
        pass
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_limitation_list: list[Limitation] = result.scalars().all()
    limitation_list = [
        ExistLimitation.from_orm(orm_limitation)
        for orm_limitation in orm_limitation_list
    ]
    return limitation_list


async def read_limitations_joined(
    category_id: Optional[UUID] = None,
    group_id: Optional[UUID] = None,
    period: Optional[UUID] = None,
    async_session_maker: sessionmaker = get_session_maker(),
) -> list[ExtendLimitation]:
    query: Select = select(Limitation, Category, Group)
    query = query.join_from(Limitation, Category,
                            Limitation.category_id == Category.id)
    query = query.join_from(Limitation, Group, Limitation.group_id == Group.id)
    if category_id is not None:
        query = query.where(Limitation.category_id == category_id)
        pass
    if group_id is not None:
        query = query.where(Limitation.group_id == group_id)
        pass
    if period is not None:
        query = query.where(Limitation.period == period)
        pass
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_extend_limitation_list: list[JoinedLimitation] = result.fetchall()
    extend_limitation_list = [
        ExtendLimitation(
            **ExistLimitation.from_orm(orm_extend_limitation.Limitation).dict(),
            category=ExistCategory.from_orm(orm_extend_limitation.Category),
            group=ExistGroup.from_orm(orm_extend_limitation.Group),
        )
        for orm_extend_limitation in orm_extend_limitation_list
    ]
    return extend_limitation_list


async def update_limitation():
    pass


async def delete_limitation(
    limitation_id: UUID, async_session_maker: sessionmaker = get_session_maker()
) -> None:
    query: Delete = delete(Limitation)
    query = query.where(Limitation.id == limitation_id)
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            await async_session.execute(query)
            pass
        pass
    return None
