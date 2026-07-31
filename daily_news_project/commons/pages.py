from fastapi import Query
from uvicorn.lifespan import off


async def page_params(
        offset: int = Query(0, ge=0, description='跳过行数'),
        limit: int = Query(10, ge=10, le=50, description='每页行数')
):
    return {
        "offset": offset,
        "limit": limit
    }

async def page_info(
        page: int = Query(1, ge=1, description='页码'),
        page_size: int = Query(10, alias='pageSize' ,ge=10, le=50, description='每页行数')
):
    offset = (page - 1) * page_size
    return {
        "offset": offset,
        "limit": page_size
    }