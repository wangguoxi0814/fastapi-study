from fastapi import Query


async def page_params(
        offset: int = Query(0, ge=0, description='跳过行数'),
        limit: int = Query(10, ge=10, le=50, description='每页行数')
):
    return {
        "offset": offset,
        "limit": limit
    }