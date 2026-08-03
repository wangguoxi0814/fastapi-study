from fastapi import FastAPI
from routers import news, users, favorite
from fastapi.middleware.cors import CORSMiddleware

from utils.exception_handlers import register_error_handlers

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # 允许的源，开发阶段允许所有源，生产环境需要指定源
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],     # 允许的请求方法
    allow_headers=["*"],     # 允许的请求头
)

# 注册全局异常处理器
register_error_handlers(app)


@app.get("/")
async def root():
    return {"message": "Welcome to Daily News"}

# 挂载路由/注册路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
