
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from commons.pages import page_params, page_info
from crud import news
from config.db_conf import get_db

router = APIRouter(prefix="/api/news", tags=['news'])

@router.get('/categories')
async def get_categories(page_params: dict = Depends(page_params), db: AsyncSession = Depends(get_db)):
    categories = await news.get_categories(db, **page_params)
    return {
        "code": 200,
        "message": "success",
        "data": categories
    }

@router.get('/list')
async def get_news_list(category_id: int = Query(alias='categoryId', description="分类ID"),
                        page_info: dict = Depends(page_info),
                        db: AsyncSession = Depends(get_db)):
    news_list = await news.get_news_list(db, category_id, **page_info)
    total = await news.get_news_count(db, category_id)
    has_more = page_info['offset'] + len(news_list) < total
    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": news_list,
            "total": total,
            "hasMore": has_more
        }
    }