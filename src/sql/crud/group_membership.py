from typing import Optional
from uuid import UUID

from sqlalchemy import select, delete, update
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import Select, Delete, Update

from ..database import get_session_maker
from ..models.group import Group
from ..models.group_membership import GroupMembership, JoinedGroupMembership
from ..models.user import User
from ..schemas.group import ExistGroup
from ..schemas.group_membership import ExtendGroupMembership, NewGroupMembership, ExistGroupMembership
from ..schemas.user import ExistUser


async def create_group_memberships(
    new_group_memberships: list[NewGroupMembership],
    async_session_maker: sessionmaker = get_session_maker(),
) -> list[ExistGroupMembership]:
    new_orm_group_memberships = [
        GroupMembership(**new_group_membership.dict())
        for new_group_membership in new_group_memberships
    ]
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            async_session.add_all(new_orm_group_memberships)
            pass
        pass
    group_memberships = [
        ExistGroupMembership.from_orm(new_orm_group_membership)
        for new_orm_group_membership in new_orm_group_memberships
    ]
    return group_memberships


async def read_group_membership(
    id: UUID, async_session_maker: sessionmaker = get_session_maker(),
) -> Optional[ExistGroupMembership]:
    group_membership: ExistGroupMembership = None
    query: Select = select(GroupMembership)
    query = query.where(GroupMembership.id == id)
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_group_membership_list: list[GroupMembership] = result.scalars().all()
    if orm_group_membership_list:
        group_membership = \
            ExistGroupMembership.from_orm(orm_group_membership_list[0])
        pass
    return group_membership


async def read_group_membership_joined(
    id: UUID, async_session_maker: sessionmaker = get_session_maker(),
) -> Optional[ExistGroupMembership]:
    extend_group_membership: ExtendGroupMembership = None
    query: Select = select(GroupMembership, Group, User)
    query = query.join_from(GroupMembership, Group,
                            GroupMembership.group_id == Group.id)
    query = query.join_from(GroupMembership, User,
                            GroupMembership.user_id == User.id)
    query = query.where(GroupMembership.id == id)
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_extend_group_membership_list: \
        list[JoinedGroupMembership] = result.fetchall()
    if orm_extend_group_membership_list:
        orm_extend_group_membership = orm_extend_group_membership_list[0]
        extend_group_membership = \
            ExtendGroupMembership(
                **ExistGroupMembership.from_orm(orm_extend_group_membership.GroupMembership).dict(),
                group=ExistGroup.from_orm(orm_extend_group_membership.Group),
                user=ExistUser.from_orm(orm_extend_group_membership.User),
            )
        pass
    return extend_group_membership


async def read_group_memberships(
    group_id: UUID = None,
    user_id: UUID = None,
    async_session_maker: sessionmaker = get_session_maker(),
) -> list[ExistGroupMembership]:
    query: Select = select(GroupMembership)
    if group_id is not None:
        query = query.where(GroupMembership.group_id == group_id)
        pass
    if user_id is not None:
        query = query.where(GroupMembership.user_id == user_id)
        pass
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_group_membership_list: list[GroupMembership] = result.scalars().all()
    group_member_ship_list = [
        ExistGroupMembership.from_orm(orm_group_membership)
        for orm_group_membership in orm_group_membership_list
    ]
    return group_member_ship_list


async def read_group_memberships_joined(
    group_id: UUID = None,
    user_id: UUID = None,
    async_session_maker: sessionmaker = get_session_maker(),
) -> list[ExtendGroupMembership]:
    query: Select = select(GroupMembership, Group, User)
    query = query.join_from(GroupMembership, Group,
                            GroupMembership.group_id == Group.id)
    query = query.join_from(GroupMembership, User,
                            GroupMembership.user_id == User.id)
    if group_id is not None:
        query = query.where(GroupMembership.group_id == group_id)
        pass
    if user_id is not None:
        query = query.where(GroupMembership.user_id == user_id)
        pass
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_extend_group_membership_list: list[JoinedGroupMembership] = result.fetchall(
    )
    extend_group_membership_list = [
        ExtendGroupMembership(
            **ExistGroupMembership.from_orm(orm_extend_group_membership.GroupMembership).dict(),
            group=ExistGroup.from_orm(orm_extend_group_membership.Group),
            user=ExistUser.from_orm(orm_extend_group_membership.User),
        )
        for orm_extend_group_membership in orm_extend_group_membership_list
    ]
    return extend_group_membership_list


async def update_group_membership(
    group_membership: ExistGroupMembership,
    async_session_maker: sessionmaker = get_session_maker(),
) -> None:
    query: Update = update(GroupMembership)
    query = query.where(GroupMembership.id == group_membership.id)
    query = query.values(**group_membership.dict())
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            await async_session.execute(query)
            pass
        pass
    return None


async def delete_group_membership(
    group_membership_id: UUID,
    async_session_maker: sessionmaker = get_session_maker(),
) -> None:
    query: Delete = delete(GroupMembership)
    query = query.where(GroupMembership.id == group_membership_id)
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            await async_session.execute(query)
            pass
        pass
    return None
