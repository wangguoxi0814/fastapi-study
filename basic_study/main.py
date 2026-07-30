from fastapi import FastAPI, Path, Query
from pydantic import BaseModel

from orm.sql_alchemy_init import lifespan, router

app = FastAPI(lifespan=lifespan)
app.include_router(router)

import responses  # noqa: E402
import exception_responses
import middlewares
import depends

@app.get('/book/{id}')
def get_book(id: int = Path(..., max_length=21, min_length=1)):
    return f'id:{id}的数据已找到'

@app.get('/books/list')
def query_book(
        page_index: int = Query(0, lte=100000),
        page_size: int = Query(10, lte=1000)
):
    return f'第{page_index + 1}页的{page_size}条数据已找到'

class User(BaseModel):
    username: str
    password: str

@app.post('/user/register')
def register_user(user: User):
    return {'username': user.username, 'password': '****'}


