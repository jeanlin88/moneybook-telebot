from typing import Optional
from uuid import UUID

from sqlalchemy import select, delete, update
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import Select, Delete, Update

from ..database import get_session_maker
from ..models.group import Group, JoinedGroup
from ..models.group_membership import GroupMembership
from ..models.user import User
from ..schemas.group import ExistGroup, ExtendGroup
from ..schemas.group import ExistGroup, NewGroup
from ..schemas.user import ExistUser


async def create_group(
    new_group: NewGroup, async_session_maker: sessionmaker = get_session_maker()
) -> ExistGroup:
    new_orm_group = Group(**new_group.dict())
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            async_session.add(new_orm_group)
            pass
        pass
    new_group = ExistGroup.from_orm(new_orm_group)
    return new_group


async def read_group(
    id: UUID = None,
    telegram_id: int = None,
    async_session_maker: sessionmaker = get_session_maker(),
) -> Optional[ExistGroup]:
    group: ExistGroup = None
    query: Select = select(Group)
    if id is not None:
        query = query.where(Group.id == id)
        pass
    elif telegram_id is not None:
        query = query.where(Group.telegram_id == telegram_id)
        pass
    else:
        return None
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_group_list: list[Group] = result.scalars().all()
    if orm_group_list:
        group = ExistGroup.from_orm(orm_group_list[0])
        pass
    return group


async def read_group_joined(
    id: UUID = None,
    telegram_id: int = None,
    async_session_maker: sessionmaker = get_session_maker(),
) -> Optional[ExtendGroup]:
    extend_group: ExtendGroup = None
    query: Select = select(Group, User)
    query = query.join_from(Group, User, Group.admin_user_id == User.id)
    if id is not None:
        query = query.where(Group.id == id)
        pass
    elif telegram_id is not None:
        query = query.where(Group.telegram_id == telegram_id)
        pass
    else:
        return None
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_extend_group_list: list[JoinedGroup] = result.fetchall()
    if orm_extend_group_list:
        orm_extend_group = orm_extend_group_list[0]
        extend_group = ExtendGroup(
            **ExistGroup.from_orm(orm_extend_group.Group).dict(),
            admin_user=ExistUser.from_orm(orm_extend_group.User),
        )
        pass
    return extend_group


async def read_groups(
    admin_user_id: UUID = None,
    async_session_maker: sessionmaker = get_session_maker(),
) -> list[ExtendGroup]:
    query: Select = select(Group)
    if admin_user_id is not None:
        query = query.where(Group.admin_user_id == admin_user_id)
        pass
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_group_list: list[Group] = result.scalars().all()
    group_list = [
        ExistGroup.from_orm(orm_group)
        for orm_group in orm_group_list
    ]
    return group_list


async def read_groups_joined(
    admin_user_id: UUID = None,
    async_session_maker: sessionmaker = get_session_maker(),
) -> list[ExtendGroup]:
    query: Select = select(Group, User)
    query = query.join_from(Group, User)
    if admin_user_id is not None:
        query = query.where(Group.admin_user_id == admin_user_id)
        pass
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_extend_group_list: list[JoinedGroup] = result.fetchall()
    extend_group_list = [
        ExtendGroup(
            **ExistGroup.from_orm(orm_extend_group.Group).dict(),
            admin_user=ExistUser.from_orm(orm_extend_group.User),
        )
        for orm_extend_group in orm_extend_group_list
    ]
    return extend_group_list


async def read_or_create_group(group_info: NewGroup) -> ExtendGroup:
    group = await read_group_joined(telegram_id=group_info.telegram_id)
    if group is None:
        group_id = (await create_group(new_group=group_info)).id
        group = await read_group_joined(id=group_id)
        pass
    return group


async def read_user_joined_groups(
    user_id: UUID,
    async_session_maker: sessionmaker = get_session_maker(),
) -> list[ExtendGroup]:
    sub_query: Select = select(GroupMembership.group_id)
    sub_query = sub_query.where(GroupMembership.user_id == user_id)
    query: Select = select(Group, User)
    query = query.join_from(Group, User, Group.admin_user_id == User.id)
    query = query.where(Group.id.in_(sub_query))
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_extend_group_list: list[JoinedGroup] = result.fetchall()
    group_list = [
        ExtendGroup(
            **ExistGroup.from_orm(orm_extend_group.Group).dict(),
            admin_user=ExistUser.from_orm(orm_extend_group.User),
        )
        for orm_extend_group in orm_extend_group_list
    ]
    return group_list


async def update_group(
    update_group: ExistGroup,
    async_session_maker: sessionmaker = get_session_maker(),
) -> None:
    query: Update = update(Group)
    query = query.where(Group.id == update_group.id)
    query = query.values(**update_group.dict())
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            await async_session.execute(query)
            pass
        pass
    return None


async def delete_group(
    group_id: UUID,
    async_session_maker: sessionmaker = get_session_maker(),
) -> None:
    query: Delete = delete(Group)
    query = query.where(Group.id == group_id)
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            await async_session.execute(query)
            pass
        pass
    return None
