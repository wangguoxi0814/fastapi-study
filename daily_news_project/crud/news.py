from sqlalchemy import select, func, update
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

async def get_news_detail(db: AsyncSession, news_id: int):
    stmt = await db.execute(
        select(News).where(News.id == news_id)
    )
    return stmt.scalar_one_or_none()

async def increase_news_views(db: AsyncSession, news_id: int):
    update_ =  update(News).where(News.id == news_id).values(views1=News.views + 1)
    stmt = await db.execute(update_)
    return stmt.rowcount

async def get_related_news_list(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    stmt = await db.execute(
        select(News)
        .where(
            News.id != news_id,
            News.category_id == category_id
        )
        .order_by(
            News.views.desc(),  # 默认升序
            News.publish_time.desc()
        )
        .limit(limit)
    )
    return stmt.scalars().all()