from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, delete, select, func
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select, Delete
from sqlalchemy.orm import sessionmaker

from ..database import get_session_maker
from ..models.category import Category
from ..models.group import Group
from ..models.record import JoinedRecord, Record
from ..models.user import User
from ..schemas.category import ExistCategory
from ..schemas.group import ExistGroup
from ..schemas.record import ExistRecord, ExtendRecord, NewRecord
from ..schemas.user import ExistUser


async def create_record(
    new_record: NewRecord, async_session_maker: sessionmaker = get_session_maker()
) -> ExistRecord:
    new_orm_record = Record(**new_record.dict())
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            async_session.add(new_orm_record)
            pass
        pass
    new_record = ExistRecord.from_orm(new_orm_record)
    return new_record


async def read_record(
    record_id: UUID,
    async_session_maker: sessionmaker = get_session_maker(),
) -> Optional[ExistRecord]:
    record: ExistRecord = None
    query: Select = select(Record)
    query = query.where(Record.id == record_id)
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_recordq_list: list[Record] = result.scalars().all()
    if orm_recordq_list:
        orm_record = orm_recordq_list[0]
        record = ExistRecord.from_orm(orm_record)
        pass
    return record


async def read_record_joined(
    id: UUID,
    async_session_maker: sessionmaker = get_session_maker(),
) -> Optional[ExtendRecord]:
    extend_record: ExtendRecord = None
    query: Select = select(Record, Category, Group, User)
    query = query.join_from(
        Record, Category, Record.category_id == Category.id)
    query = query.join_from(Record, Group, Record.group_id == Group.id)
    query = query.join_from(Record, User, Record.user_id == User.id)
    if id is not None:
        query = query.where(Record.id == id)
        pass
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_extend_record_list: list[JoinedRecord] = result.fetchall()
    if orm_extend_record_list:
        orm_extend_record = orm_extend_record_list[0]
        extend_record = ExtendRecord(
            **ExistRecord.from_orm(orm_extend_record.Record).dict(),
            category=ExistCategory.from_orm(orm_extend_record.Category),
            group=ExistGroup.from_orm(orm_extend_record.Group),
            user=ExistUser.from_orm(orm_extend_record.User),
        )
        pass
    return extend_record


async def read_records(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    category_ids: list[UUID] = [],
    category_reverse: bool = False,
    date_after: Optional[date] = None,
    date_before: Optional[date] = None,
    group_id: Optional[UUID] = None,
    is_income: Optional[bool] = None,
    user_id: Optional[UUID] = None,
    order_by_columns: list[Column] = [],
    async_session_maker: sessionmaker = get_session_maker(),
) -> list[ExistRecord]:
    query: Select = select(Record)
    if category_ids:
        query = query.where(
            Record.category_id.not_in(category_ids) if category_reverse
            else Record.category_id.in_(category_ids)
        )
        pass
    if date_after is not None:
        query = query.where(Record.record_date >= date_after)
        pass
    if date_before is not None:
        query = query.where(Record.record_date <= date_before)
        pass
    if group_id is not None:
        query = query.where(Record.group_id == group_id)
        pass
    if is_income is not None:
        query = query.where(Record.is_income == is_income)
        pass
    if user_id is not None:
        query = query.where(Record.user_id == user_id)
        pass
    query = query.order_by(*order_by_columns)
    if limit is not None and offset is not None:
        query = query.limit(limit).offset(offset)
        pass
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_record_list: list[Record] = result.scalars().all()
    record_list = [
        ExistRecord.from_orm(orm_record)
        for orm_record in orm_record_list
    ]
    return record_list


async def read_records_joined(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    category_ids: list[UUID] = [],
    category_reverse: bool = False,
    date_after: Optional[date] = None,
    date_before: Optional[date] = None,
    group_id: Optional[UUID] = None,
    is_income: Optional[bool] = None,
    user_id: Optional[UUID] = None,
    order_by_columns: list[Column] = [],
    async_session_maker: sessionmaker = get_session_maker(),
) -> list[ExtendRecord]:
    query: Select = select(Record, Category, Group, User)
    query = query.join_from(
        Record, Category, Record.category_id == Category.id)
    query = query.join_from(Record, Group, Record.group_id == Group.id)
    query = query.join_from(Record, User, Record.user_id == User.id)
    if category_ids:
        query = query.where(
            Record.category_id.not_in(category_ids) if category_reverse
            else Record.category_id.in_(category_ids)
        )
        pass
    if date_after is not None:
        query = query.where(Record.record_date >= date_after)
        pass
    if date_before is not None:
        query = query.where(Record.record_date <= date_before)
        pass
    if group_id is not None:
        query = query.where(Record.group_id == group_id)
        pass
    if is_income is not None:
        query = query.where(Record.is_income == is_income)
        pass
    if user_id is not None:
        query = query.where(Record.user_id == user_id)
        pass
    query = query.order_by(*order_by_columns)
    if limit is not None and offset is not None:
        query = query.limit(limit).offset(offset)
        pass
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_extend_record_list: list[JoinedRecord] = result.fetchall()
    extend_record_list = [
        ExtendRecord(
            **ExistRecord.from_orm(orm_extend_record.Record).dict(),
            category=ExistCategory.from_orm(orm_extend_record.Category),
            group=ExistGroup.from_orm(orm_extend_record.Group),
            user=ExistUser.from_orm(orm_extend_record.User),
        )
        for orm_extend_record in orm_extend_record_list
    ]
    return extend_record_list


async def read_records_total_count(
    category_ids: list[UUID] = [],
    category_reverse: bool = False,
    date_after: Optional[date] = None,
    date_before: Optional[date] = None,
    group_id: Optional[UUID] = None,
    is_income: Optional[bool] = None,
    user_id: Optional[UUID] = None,
    async_session_maker: sessionmaker = get_session_maker(),
) -> int:
    query: Select = select(func.count('*'))
    query = query.select_from(Record)
    if category_ids:
        query = query.where(
            Record.category_id.not_in(category_ids) if category_reverse
            else Record.category_id.in_(category_ids)
        )
        pass
    if date_after is not None:
        query = query.where(Record.record_date >= date_after)
        pass
    if date_before is not None:
        query = query.where(Record.record_date <= date_before)
        pass
    if group_id is not None:
        query = query.where(Record.group_id == group_id)
        pass
    if is_income is not None:
        query = query.where(Record.is_income == is_income)
        pass
    if user_id is not None:
        query = query.where(Record.user_id == user_id)
        pass
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    count_list: int = result.scalars().all()[0]
    return count_list


async def update_record():
    pass


async def delete_record(
    record_id: UUID,
    async_session_maker: sessionmaker = get_session_maker(),
) -> None:
    query: Delete = delete(Record)
    query = query.where(Record.id == record_id)
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            await async_session.execute(query)
            pass
        pass
    return None
