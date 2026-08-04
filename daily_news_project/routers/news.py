
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

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
    news_list = await news.get_news_list(db, category_id=category_id, **page_info)
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

@router.get('/detail')
async def get_news_detail(news_id: int = Query(..., alias="id", description="新闻ID"), db: AsyncSession = Depends(get_db)):
    news_detail = await news.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=500, detail="新闻不存在!")
    view_res = await news.increase_news_views(db, news_id)
    if not view_res:
        raise HTTPException(status_code=500, detail="更新新闻浏览量失败!")
    related_news = await news.get_related_news_list(db, news_detail.id, news_detail.category_id)

    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news
        }
    }