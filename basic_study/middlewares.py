from basic_study.main import app

# 中间件
# 作用：统一拦截请求，可以做日志记录、权限校验等
# 执行顺序：
## 按声明顺序执行，洋葱模型
## 如果需要通过显示参数指定执行顺序，需要自定义封装

@app.middleware("http")
async def auth_middleware(request, call_next):
    print('request auth start...')
    response = await call_next(request)
    print('request auth end...')
    return response

@app.middleware("http")
async def log_middleware(request, call_next):
    print('request log start...')
    response = await call_next(request)
    print('request log end...')
    return response


