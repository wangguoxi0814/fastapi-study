from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app):
    print('服务启动...')
    yield
    print('服务停止')
