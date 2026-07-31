from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import Category


async def get_categories(db: AsyncSession, offset: int = 0, limit: int = 10):
    stmt = await db.execute(
        select(Category).offset(offset).limit(limit)
    )
    return stmt.scalars().all()
