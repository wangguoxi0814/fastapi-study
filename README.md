# FastAPI Study

FastAPI 学习项目，涵盖路由、请求参数、响应格式、异常处理、中间件、依赖注入、ORM 等核心功能。

## 项目结构

```
fastapi-study/
├── main.py                 # 应用入口，路由注册
├── responses.py            # 响应格式示例（JSON、HTML、File）
├── exception_responses.py  # 异常处理示例
├── middlewares.py           # 中间件示例
├── depends.py              # 依赖注入示例
├── orm/
│   ├── sql_alchemy_init.py # SQLAlchemy ORM 完整示例
│   └── __init__.py
└── files/                  # 静态资源
```

## 环境要求

- Python 3.10+
- MySQL 8.0+

## 安装依赖

```bash
pip install fastapi uvicorn sqlalchemy aiomysql
```

## 启动服务

```bash
# 开发环境（热重载）
uvicorn main:app --reload --port 8000

# 访问 Swagger 文档
http://localhost:8000/docs
```

## 功能模块

### 1. 路由与请求参数

```python
# 路径参数
@app.get('/book/{id}')
def get_book(id: int = Path(..., max_length=21, min_length=1))

# 查询参数
@app.get('/books/list')
def query_book(page_index: int = Query(0, lte=100000), page_size: int = Query(10, lte=1000))

# 请求体
@app.post('/user/register')
def register_user(user: User)  # User 为 Pydantic BaseModel
```

### 2. 响应格式

| 路由 | 响应类型 | 说明 |
|------|---------|------|
| `GET /role/info` | `response_model=RoleModel` | Pydantic 模型校验响应 |
| `GET /role/{role_id}` | `JSONResponse` | JSON 响应 |
| `GET /role/html_info/{role_id}` | `HTMLResponse` | HTML 响应 |
| `GET /role/img/{role_id}` | `FileResponse` | 文件下载 |

### 3. 异常处理

```python
from fastapi import HTTPException

@app.get("/product/{product_id}")
def product_detail(product_id: int):
    if product_id not in ids:
        raise HTTPException(status_code=404, detail="Product not found")
```

### 4. 中间件

中间件按声明顺序执行，采用**洋葱模型**：

```
请求进入 → auth_middleware → log_middleware → 路由处理 → log_middleware → auth_middleware → 响应
```

```python
@app.middleware("http")
async def auth_middleware(request, call_next):
    # 请求前逻辑
    response = await call_next(request)
    # 请求后逻辑
    return response
```

### 5. 依赖注入

公共查询参数通过 `Depends` 复用：

```python
async def page_info(
    page_index: int = Query(0, ge=0),
    page_size: int = Query(10, ge=10, le=50)
):
    return {"page_index": page_index, "page_size": page_size}

@app.get('/promotion/list')
async def promotion_list(page_info: dict = Depends(page_info)):
    return page_info
```

### 6. SQLAlchemy ORM

基于 SQLAlchemy 2.0 异步模式，集成 MySQL。

#### 数据库配置

```python
DB_NAME = 'fastapi_study'
SQLALCHEMY_DATABASE_URL = f"mysql+aiomysql://root:123456@localhost:3306/{DB_NAME}"
```

#### 数据模型

```python
class Book(Base):
    __tablename__ = 'book'
    id: Mapped[int] = mapped_column(primary_key=True)
    book_name: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Float)
    publisher: Mapped[str] = mapped_column(String(255))
```

#### ORM 接口

| 方法 | 路由 | 说明 |
|------|------|------|
| GET | `/book/list` | 查询图书列表（支持条件筛选） |
| GET | `/book/{book_id}` | 根据 ID 查询单本图书 |
| POST | `/book/insert` | 批量插入测试数据 |
| PUT | `/book/update/{book_id}` | 更新图书信息 |
| DELETE | `/book/delete/{book_id}` | 删除图书 |
| GET | `/book/price/total` | 价格统计（sum/avg/max/min） |
| GET | `/book/page` | 分页查询 |

#### ORM 生命周期管理

使用 `yield` 依赖注入统一管理事务：

```python
async def create_session():
    async with async_session() as session:
        try:
            yield session           # 路由函数在此暂停执行
            await session.commit()  # 路由正常结束，自动提交
        except Exception:
            await session.rollback()  # 路由异常，自动回滚
            raise
        finally:
            await session.close()   # 无论如何，关闭连接
```

#### 关键概念

- **`flush` vs `commit`**：`flush` 将 SQL 发送到数据库但不提交事务（可获取自增 ID），`commit` 正式提交事务
- **`session.delete()`**：要求对象必须是从数据库查询出来的（persistent 状态），不支持传入新建对象
- **脏标记追踪**：ORM 对象属性被修改后自动标记为 dirty，commit 时自动生成 UPDATE SQL

## 常用命令

```bash
# 数据库迁移（首次运行）
# 执行 orm/sql_alchemy_init.py 中的 create_table() 建表

# 插入测试数据
curl -X POST http://localhost:8000/book/insert

# 查询图书列表
curl http://localhost:8000/book/list

# 分页查询
curl "http://localhost:8000/book/page?page=1&page_size=10"

# 更新图书
curl -X PUT http://localhost:8000/book/update/1 \
  -H "Content-Type: application/json" \
  -d '{"book_name": "石头记"}'

# 删除图书
curl -X DELETE http://localhost:8000/book/delete/1
```
