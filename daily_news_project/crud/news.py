from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import Category, News


async def get_categories(db: AsyncSession, offset: int = 0, limit: int = 10):
    stmt = await db.execute(
        select(Category).offset(offset).limit(limit)
    )
    return stmt.scalars().all()

async def get_news_list(db: AsyncSession, category_id: int, offset: int = 0, limit: int = 10):
    stmt = await db.execute(
        select(News).where(News.category_id == category_id).offset(offset).limit(limit)
    )
    return stmt.scalars().all()

async def get_news_count(db: AsyncSession, category_id: int):
    stmt = await db.execute(select(func.count(News.id)).where(News.category_id == category_id))
    return stmt.scalar_one()