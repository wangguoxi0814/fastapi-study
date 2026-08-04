# FastAPI Study Note

## 第一章 FastAPI基本使用
### 服务启动
```shell
    pip install uvicorn
    cd .../fastapi-study/basic_study
    uvicorn main:app --reload
```
- main: 模块名
- app: FastAPI实例名
- --reload: 热加载
- 访问：`http://127.0.0.1:8000`
- 接口文档访问：`http://127.0.0.1:8000/docs`

### 接口声明
#### 路径参数接口
- 适用：get\post\put\delete请求
- 示例：
    ```python
    @app.get('/book/{id}')
    def get_book(id: int = Path(..., max_length=21, min_length=1)):
          return f'id:{id}的数据已找到'
    ```
    - Path类型注解可用辅助参数校验。...表示必需，还提供max_length、min_length等等
#### 查询参数接口
- 适用：get\post\put\delete请求
- 示例:
  ```python
    @app.get('/books/list')
    def query_book(
            page_index: int = Query(0, lte=100000),
            page_size: int = Query(10, lte=1000)
    ):
        return f'第{page_index + 1}页的{page_size}条数据已找到'
  ```
  - Query提供对查询参数的默认值设置和限制条件, 但非必需
  - URL中无需声明参数
#### 请求体
- 适用：put/post
- 示例：
  ```python
    from pydantic import BaseModel
    
    class User(BaseModel):
        username: str
        password: str
  
    @app.post('/user/register')
    def register_user(user: User):
        return {'username': user.username, 'password': '****'}
  ```
  - 参数为一个复杂对象，需要继承pydantic的BaseModel
  - 可以通过pydantic的Field为字段设置默认值，校验等
  - 只有pydantic模型可以作为请求体，SQLAlchemy ORM模型不支持
  - 一个接口可以有多个pydantic模型作为请求体，每个模型作为JSON中的一个field嵌套传入

#### 响应
FastAPI支持多种请求参数，默认是JSON。FastAPI会自动将python的dict、列表、pydantic模型,经由`jsonable_encoder`转化为JSON,并包装为
JSONResponse返回。
- 支持的响应类型：
  - **JSONResponse**：返回JSON
  - **HTMLResponse**：返回HTML
  - PlainTextReponse：返回纯文本
  - **FileReponse**：返回文件下载
  - StreamingResponse：生成器函数返回数据,适合大文件
  - RedirectResponse: 重定向
- 响应类型指定：
  - 示例:[responses.py](../basic_study/responses.py)
  - 路由装饰器的`reponse_class`指定
  - 直接返回对应的类
- 自定义响应格式
  - 可以自定义pydantic模型，作为返回的数据结构
  - 使用：
  - 示例:[responses.py](../basic_study/responses.py)
  - 装饰器的`response_model`指定，自带校验
- 异常响应(exception_reponses.py)
  - [代码exception_responses.py](../basic_study/exception_responses.py)
  - `HTTPException(status_code=xxx, detail=xxx)`

### 中间件
- 作用：统一拦截处理逻辑
- 场景：日志记录、权限校验
- 装饰器类型：1. 装饰器函数中间件 2. 类中间件
  - 装饰器函数中间件代码：[middlewares.py](../basic_study/middlewares.py)
  - 装饰器函数中间件时适应单场景
  - 类中间件要继承 `BaseHTTPMiddleware`实现`dispatch`方法，适合复杂，复用度高的场景
  - 类中间件代码见：[middlewares.py](../daily_news_project/commons/middlewares.py)
- 装饰器函数中间件逻辑：
  - 添加中间件底层是一个stack，所以先添加的middleware在栈底，最后执行。也就是按before按添加逆序执行，after按添加顺序执行。类中间件和函数装饰器中间件混杂时也遵循这个原则
  - 查看中间件执行链方法：`app.middleware_stack`获取所有的中间件列表，包括`FastAPI`自带中间件,但函数装饰器中间件在链中会显示`BaseHTTPMiddleware`,如果需要更好区分，可以自己遍历重新封装
，示例代码:[main.py](../daily_news_project/main.py)中的`root()`。需要注意的是，这个stack是懒加载，需要发送请求后才能够获取到执行链，如果只是服务已启动，获取到的是None
  - 查看用户自定义中间件执行链：`app.user_middleware`,只包含用户自定义中间件执行链,更纯净，且无需发送请求初始化。示例代码:[main.py](../daily_news_project/main.py)中的`root()`
  - 方法要定义为async/await。middleware的call_next返回的是协程对象，没有await不会执行，影响middleware的打印顺序，middleware函数必须声明为async\await
  - 默认拦截所有的路由，静态资源请求
  - 如果需要增加显示order参数编排中间件执行顺序，需要自定义封装
- 怎么自定义拦截规则？
  - 中间件默认拦截所有请求，如果需要自定义，需要自行实现代码判断处理

### 依赖注入
- 作用: 抽取公共参数逻辑,按需使用
- 使用：
  - 代码: [depends.py](../basic_study/depends.py)
  - 依赖项：一个函数，返回dict用于传给Depends。普通函数和异步函数都可以，FastAPI底层会区分。
  - 声明依赖项：目标方法参数的类型注解声明为Depends
- 场景：
  - 数据库会话对象依赖项
  - 通用分页参数依赖项
#### 数据库依赖项是如何自动提交事务原理解析
- 数据库注入代码示例: [sql_alchemy_init.py](../basic_study/orm/sql_alchemy_init.py)
- 注入会话时，`Depends`的函数是一个生成器函数，FastAPI在解析依赖时，执行逻辑大概如下：
  ```python
    # FastAPI 内部大致逻辑
    async def resolve_dependency(dependency_func):
        # 1. 创建生成器
        gen = dependency_func()           # create_session() 返回生成器对象

        # 2. 执行到 yield，获取 session
        session = await gen.__anext__()   # 执行 yield 之前的代码，暂停在 yield 处

        return session, gen  # 把 session 交给路由函数，gen 保存起来
  ```
- FastAPI在解析完依赖后，会执行请求，在执行完请求后，会执行执行器的`__anext__()`方法,大致逻辑如下：
  ```python
        # FastAPI 内部大致逻辑
    async def handle_request():
        session, gen = await resolve_dependency(create_session)

        try:
            result = await route_function(session)  # 执行路由函数
            return result
        except Exception:
            await gen.athrow(Exception)  # 触发 except 分支（rollback）
        finally:
            await gen.__anext__()        # 执行 yield 之后的代码（commit + close）
  ```
最后执行生成器的下一步，`create_session()`上下文继续执行，从而自动提交事务

### FastAPI多参数解析
```python
async def page_info(
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(10, ge=10, le=50, description="每页条数"),
):
    return {
        "page": page,
        "page_size": page_size
    }

# 6. 依赖项
async def create_session():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise  # 重新抛出异常，让 FastAPI 正常处理
        finally:
            await session.close()

async def search_book(book_dto: BookDTO, page_info: dict = Depends(page_info), db: AsyncSession = Depends(create_session)):
```
在上面的代码中：
- 请求体是: `book_dto`,只有pydantic的模型可以作为请求体
- 请求参数是: `page_info`, `page_info()`函数有2个参数，均会被解析为请求参数
- db依赖项: 依赖项`create_session()`没有入参，因此不会被解析为请求参数

## lifespan生命周期函数
- 示例: [sql_alchemy_init.py:lifespan](../basic_study/orm/sql_alchemy_init.py)
- 原理: 
  - 异步上下文管理器，通过`FastAPI(lifespan=lifespan)`注册后，在服务启动时会执行`__aenter__()`,服务停止时执行`__aexit__()`
- 老版生命周期函数（已废弃）: 
  - `@app.on_event("startup")` 启动时执行
  - `@app.on_event("shutdown")` 停止时执行
- 一个FastAPI实例只可以注册一个lifespan，lifespan函数参数是`FastAPI实例`
- 如果需要组合多个生命周期逻辑，可用`AsyncExitStack`组合

## 第二章 FastAPI进阶
### 模块化路由
- 示例:
- `APIRouter`声明路由, FastAPI示例注册路由
- 作用：按模块划分路由，避免混乱

### 跨域处理
- 跨域是浏览器安全机制，只允许同源的请求，前端和后端的协议、域名、端口任一不同，就会触发跨域
- 处理：使用内置的`CORSMiddleware`, 再通过`FastAPI`的`add_middleware`添加
- 示例：
  ```python
        app.add_middleware(
          CORSMiddleware,
          allow_origins=["*"],     # 允许的源，开发阶段允许所有源，生产环境需要指定源
          allow_credentials=True,  # 允许携带cookie
          allow_methods=["*"],     # 允许的请求方法
          allow_headers=["*"],     # 允许的请求头
        )
  ```
- 其他处理跨域方案：
  - Nginx反向代理,配置跨域响应头
    1. 浏览器检查页面Origin和请求目标Origin是否一致，不一致则判定为跨域请求
    2. 跨域请求(如果是GET请求，会直接发送请求本身。如果是POST、PUT、DELETE请求，会先发送预检请求(OPTIONS))会发送到Nginx，Nginx将请求给转发给服务器
    3. 服务器响应给Nginx,Nginx给响应头添加跨域响应头，返回给浏览器

### 全局异常处理
- 示例：[exception_handlers.py](../daily_news_project/utils/exception_handlers.py)
- 异常捕获顺序：
  - 无关注册顺序，只会根据异常的MRO顺序捕获，即便`Exception`注册在最前面，发生其子异常时，也会交由具体的异常处理器处理。
- 事务影响: 
  不会对事务找出影响。执行顺序如下：
  - 在发送异常后，会执行db依赖项的except分支，执行`rollback()`，再会把异常给全局异常处理器，响应异常