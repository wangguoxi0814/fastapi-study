# FastAPI Study Note

## 第一章 FastAPI基本使用
### 服务启动
```shell
    pip install uvicorn
    uvicorn main:app --reload
```
- app: FastAPI实例名
- --reload: 热加载
- 访问：`http://127.0.0.1:8000`
- 接口文档访问：`http://127.0.0.1:8000/docs`

### 接口声明
#### 路径参数接口
- 适用：get/delete请求
- 示例：
    ```python
    @app.get('/book/{id}')
    def get_book(id: int = Path(..., max_length=21, min_length=1)):
          return f'id:{id}的数据已找到'
    ```
    - Path类型注解可用辅助参数校验。...表示必需，还提供max_length、min_length等等
#### 查询参数接口
- 适用：get请求
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
fastapi支持多种请求参数，默认是JSON。fastapi会自动将python的dict、列表、pydantic模型,经由jsonable_encoder转化为JSON,并包装为
JSONResponse返回。
- 支持的响应类型：
  - **JSONResponse**：返回JSON
  - **HTMLResponse**：返回HTML
  - PlainTeHTMLResponsextReponse：返回纯文本
  - **FileReponse**：返回文件下载
  - StreamingResponse：生成器函数返回数据,适合大文件
  - RedirectResponse: 重定向
- 响应类型指定：
  - [代码responses.py](../responses.py)
  - 路由装饰器的`reponse_class`指定
  - 直接返回对应的类
- 自定义响应格式
  - 可以自定义pydantic模型，作为返回的数据结构
  - 使用：
  - [代码responses.py](../responses.py)
  - 装饰器的`response_model`指定，自带校验
- 异常响应(exception_reponses.py)
  - [代码exception_responses.py](../exception_responses.py)
  - `HTTPException(status_code=xxx, detail=xxx)`

### 中间件
- 作用：统一拦截处理逻辑
- 场景：日志记录、权限校验
- 代码：[middlewares.py](../middlewares.py)
- 逻辑：
  - 洋葱模型，按声明逆序执行
  - 要定义为async/await。middleware的call_next返回的是协程对象，没有await不会执行，影响middleware的打印顺序，middleware函数必须声明为async\await
  - 默认拦截所有的路由，静态资源请求
  - 如果需要增加显示order参数编排中间件执行顺序，需要自定义封装
- 怎么自定义拦截规则？

### 依赖注入
- 作用: 抽取公共参数逻辑,按需使用
- 使用：
  - 代码: [depends.py](../depends.py)
  - 依赖项：一个函数，返回dict用于传给Depends
  - 声明依赖项：目标方法参数的类型注解声明为Depends
- 场景：
  - 数据库会话对象依赖项
  - 通用分页参数依赖项
#### 数据库依赖项是如何自动提交事务原理解析
- 数据库注入代码示例: [sql_alchemy_init.py](../orm/sql_alchemy_init.py)
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
- db依赖项: 依赖的`create_session()`没有入参，因此不会被解析为请求参数


## 第二章 SQLAlchemy集成
### SQLAlchemy集成
- 安装：`pip install "sqlalchemy[asyncio]" aiomysql`
- 代码：[sql_alchemy_init.py](../orm/sql_alchemy_init.py)
  - 创建异步数据库引擎
  - 创建数据模型（继承`DeclarativeBase`类）
  - 在FastAPI的`lifescan`中建库、建表(只有当表不存在时才会创建)
  - 基于异步引擎创建异步会话(`AsyncSession`)
  - 在router中依赖异步会话，通过`AsyncSession`对象执行SQL
- 问题：
  - 数据库异步引擎在io时会让出cpu去执行，这样会很容易让连接池耗尽吗？

### 增删改查
#### 增
- 示例：[sql_alchemy_init.py:insert_books](../orm/sql_alchemy_init.py)
- 使用:
  - 批量添加：`AsyncSession.add_all()`
  - 添加单个：`AsyncSession.add()`
  - 提交事务

#### 删
- 示例：[sql_alchemy_init.py:delete_orm & delete_by](../orm/sql_alchemy_init.py)
- 删除分为两种方式：
  - ORM思维：通过`AsyncSession.delete()`删除，在执行删除前，必须先查询出对象，再删除对象,如果不先查，执行删除会报错，视角是对象
  - SQL思维：通过`select().where()`封装查询语句，再通过`AsyncSession.execute()`执行，视角是SQL本身
  > ORM思维更方便处理级联删除，如果存在级联关系，查询出对象时，对象里已经包含了级联对象，Alchmemy底层会级联删除.
  > 而SQL思维只关注当前数据，不会级联删除，会出现数据不一致情况 

#### 改
- 示例：[sql_alchemy_init.py:update_book](../orm/sql_alchemy_init.py)
- 查询出来，直接操作ORM对象即可，在提交事务时自动更新到数据库
- 原理：**脏标记追踪**
  - 修改的对象标记为dirty
  - 提交事务时，检查所有dirty对象，生成update语句更新

#### 查
- 示例：[sql_alchemy_init.py:search_book](../orm/sql_alchemy_init.py)
- 关键点:
  - `select().where()`封装查询语句，由`AsyncSession.execute()`执行
  - 执行后的结果，再通过`ScalarResult.scalars()`转为模型对象
- 按主键查询
  - `AsyncSession.get(DelarativeMode, primary_key)`: 按主键查询，快速获取详情信息
  - `AsyncSession.query(DelarativeMode).filter(DelarativeMode.id == primary_key)`: 按主键查询，返回查询结果对象
- 条件查询
  - `==`,`!=`,`>`,`>=`,`<`,`<=`,`like`,`in_`,`not_in_`
  - `&`, `|`,`~`,逻辑运算符优先级高于`==`,`!=`,`>`等，因此在连接多个条件时，需要使用括号进行括号运算
  - `like`模糊查询通配符：`%`匹配任意字符，`_`匹配任意一个字符
- 聚合查询
  - `func.count()`,`func.sum()`,`func.avg()`,`func.max()`,`func.min()`
  - 示例: [sql_alchemy_init.py:book_statistics](../orm/sql_alchemy_init.py)
- 分页查询
  - 关键参数：`offset`,`limit`, 和mysql的limit offset语法一致
  - `offset`计算：(page - 1) * page_size
  - 示例：[sql_alchemy_init.py:search_book](../orm/sql_alchemy_init.py)

 

## lifespan生命周期函数
- 示例: [sql_alchemy_init.py:lifespan](../orm/sql_alchemy_init.py)
- 原理: 
  - 异步上下文管理器，通过`FastAPI(lifespan=lifespan)`注册后，在服务启动时会执行`__aenter__()`,服务停止时执行`__aexit__()`
- 老版生命周期函数（已废弃）: 
  - `@app.on_event("startup")` 启动时执行
  - `@app.on_event("shutdown")` 停止时执行
- 一个FastAPI实例只可以注册一个lifespan，lifespan函数参数是`FastAPI实例`
- 如果需要组合多个生命周期逻辑，可用`AsyncExitStack`组合