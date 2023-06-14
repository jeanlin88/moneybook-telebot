from typing import Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import Select, Delete

from ..database import get_session_maker
from ..models.category import Category
from ..schemas.category import ExistCategory, NewCategory


async def create_categories(
    new_categories: list[NewCategory],
    async_session_maker: sessionmaker = get_session_maker(),
) -> list[ExistCategory]:
    new_orm_categories = [
        Category(**new_category.dict())
        for new_category in new_categories
    ]
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            async_session.add_all(new_orm_categories)
            pass
        pass
    categories = [
        ExistCategory.from_orm(new_orm_category)
        for new_orm_category in new_orm_categories
    ]
    return categories


async def read_category(
    category_id: UUID,
    async_session_maker: sessionmaker = get_session_maker(),
) -> Optional[ExistCategory]:
    category: ExistCategory = None
    query: Select = select(Category)
    query = query.where(Category.id == category_id)
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_categories: list[ExistCategory] = result.scalars().all()
    if orm_categories:
        orm_category = orm_categories[0]
        category = ExistCategory.from_orm(orm_category)
        pass
    return category


async def read_categories(
    category_name_list: list[str] = [],
    async_session_maker: sessionmaker = get_session_maker(),
) -> list[ExistCategory]:
    query: Select = select(Category)
    if category_name_list:
        query = query.where(Category.name.in_(category_name_list))
        pass
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            result: ChunkedIteratorResult = await async_session.execute(query)
            pass
        pass
    orm_categories: list[ExistCategory] = result.scalars().all()
    categories = [
        ExistCategory.from_orm(orm_category)
        for orm_category in orm_categories
    ]
    return categories


async def delete_category(
    category_id: UUID,
    async_session_maker: sessionmaker = get_session_maker(),
) -> None:
    query: Delete = delete(Category)
    query = query.where(Category.id == category_id)
    async with async_session_maker() as async_session:
        async_session: AsyncSession
        async with async_session.begin():
            await async_session.execute(query)
            pass
        pass
    return None
