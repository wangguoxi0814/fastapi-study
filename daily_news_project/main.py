from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from commons.middlewares import LogMiddleware, CircuitMiddleware
from routers import news, users, favorite, history
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
@app.middleware('http')
async def ip_block_middleware(request, call_next):
    print('ip block middleware begin')
    BLOCKED_IPS = ['168.1.2.1']
    client_ip = request.client.host
    if client_ip in BLOCKED_IPS:
        return Response('IP被禁止访问', status_code=403)
    response = await call_next(request)
    print('ip block middleware end')
    return response

app.add_middleware(LogMiddleware)
app.add_middleware(CircuitMiddleware)



# 注册全局异常处理器
register_error_handlers(app)


@app.get("/")
async def root():
    middleware_name_chain = []
    current_middleware = app.middleware_stack
    while current_middleware:
        middleware_class_name = type(current_middleware).__name__
        dispatch_name = getattr(current_middleware, 'dispatch_func', middleware_class_name)
        middleware_name = f'{middleware_class_name}#{dispatch_name}'
        middleware_name_chain.append(middleware_name)
        # # 每个中间件的 app 属性指向下一个
        current_middleware = getattr(current_middleware, 'app', None)
    return {
        "message": "Welcome to Daily News",
        "middleware_stack": str(middleware_name_chain),
        "user_middleware": str(app.user_middleware),
    }

# 挂载路由/注册路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)

