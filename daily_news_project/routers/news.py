from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from commons.pages import page_params
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