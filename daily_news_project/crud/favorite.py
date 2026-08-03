from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News


async def is_news_favorite(db: AsyncSession, user_id: int, news_id: int):
    result = await db.execute(
        select(Favorite)
        .where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    )
    return result.scalar_one_or_none() is not None


async def add_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    return favorite


async def remove_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    return result.rowcount > 0


# 获取收藏列表：获取的是某个用户的收藏列表 + 分页功能
async def get_favorite_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    total_exe = await db.execute(
        select(func.count(Favorite.id))
        .where(
            Favorite.news_id == Favorite.news_id,
            Favorite.user_id == Favorite.user_id
        )
    )
    total = total_exe.scalar_one()

    rows_exe = await db.execute(
        select(News, Favorite.created_at.label("favorite_time"), Favorite.id.label("favorite_id"))
        .join(Favorite, Favorite.news_id == News.id)
        .where(
            Favorite.user_id == user_id
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = rows_exe.all()

    return rows, total

# 清空收藏列表：当前用户的收藏列表
async def remove_all_favorites(
        db: AsyncSession,
        user_id: int
):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()

    # 返回一个删除的数量
    return result.rowcount or 0