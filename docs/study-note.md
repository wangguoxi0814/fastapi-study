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
  - Query提供对查询参数的默认值设置和限制条件
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

## 第二章 SQLAlchemy集成
### SQLAlchemy集成
- 安装：`pip install "sqlalchemy[asyncio]" aiomysql`
- 代码：[sql_alchemy_init.py](../sql_alchemy_init.py)
  - 创建异步数据库引擎
  - 创建数据模型（继承`DeclarativeBase`类）
  - 在FastAPI的`lifescan`中建库、建表(只有当表不存在时才会创建)
  - 基于异步引擎创建异步会话(`AsyncSession`)
  - 在router中依赖异步会话，通过`AsyncSession`对象执行SQL
- 问题：
  - 数据库异步引擎在io时会让出cpu去执行，这样会很容易让连接池耗尽吗？

## lifespan
- lifespan：替代 deprecated 的 on_event
- @asynccontextmanager

## 