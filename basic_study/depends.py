# 依赖注入
from fastapi import Query, Depends

from main import app

# 公共参数
async def page_info(
        page_index: int = Query(0, ge=0, description="页码"),
        page_size: int = Query(10, ge= 10, le=50, description="每页条数")
):
    return {
        "page_index": page_index,
        "page_size": page_size,
    }

@app.get('/promotion/list')
async def promotion_list(page_info: dict = Depends(page_info)):
    return page_info

@app.get('/gifs/list')
async def gifs_list(page_info: dict = Depends(page_info)):
    return page_info