from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()
from sqlalchemy import DateTime, func, select, String, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# 创建异步引擎
DB_NAME = 'fastapi_study'
DB_URL = f'mysql+aiomysql://root:root@localhost:3306/{DB_NAME}?charset=utf8mb4'
DB_URL_NO_DB = 'mysql+aiomysql://root:root@localhost:3306/?charset=utf8mb4'

async_engine = create_async_engine(
    DB_URL,
    echo=True,
    pool_size=10,
    max_overflow=20
)


# 定义模型类
class Base(DeclarativeBase):
    create_date: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), default=func.now(),
                                                  comment='创建时间')
    update_date: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), onupdate=func.now(),
                                                  default=func.now(), comment='更新时间')


class Book(Base):
    __tablename__ = 'book'

    id: Mapped[int] = mapped_column(primary_key=True, comment='书籍ID')
    book_name: Mapped[str] = mapped_column(String(255), comment='书籍名称')
    author: Mapped[str] = mapped_column(String(255), comment='作者')
    publisher: Mapped[str] = mapped_column(String(255), comment='出版社')


# 3. 启动时自动建库建表
async def create_database():
    """连接 MySQL（不指定库），创建数据库（如不存在）"""
    engine = create_async_engine(DB_URL_NO_DB, echo=True)
    async with engine.begin() as conn:
        await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET utf8mb4"))
    await engine.dispose()


async def create_tables():
    """建表"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# 4. lifespan：替代 deprecated 的 on_event
@asynccontextmanager
async def lifespan(app):
    await create_database()  # 启动时建库
    await create_tables()  # 启动时建表
    yield
    await async_engine.dispose()  # 关闭时释放连接池


# 5. 创建会话
async_session = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


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


@router.get("/book/list")
async def book_list(db_session: AsyncSession = Depends(create_session)):
    print(f'db_session: {db_session}')
    result = await db_session.execute(select(Book))
    print(f'result: {result}')
    books = result.scalars().all()
    return books


@router.get('/book/detail/{id}')
async def get_by_id(id: int, db_session: AsyncSession = Depends(create_session)):
    book = await db_session.get(Book, id)
    return book


@router.get('/book/list/first')
async def get_by_id(db_session: AsyncSession = Depends(create_session)):
    result = await db_session.execute(select(Book))
    book = result.scalars().first()
    return book

class BookDTO(BaseModel):
    id: Optional[int] = None
    id_list: Optional[list[int]] = None
    book_name: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None

@router.post('/book/search')
async def search_book(book_dto: BookDTO, db: AsyncSession = Depends(create_session)):
    query = select(Book)
    if book_dto.id is not None:
        query = query.where(Book.id == book_dto.id)
    if book_dto.id_list:
        query = query.where(Book.id.in_(book_dto.id_list))
    if book_dto.author:
        query = query.where(Book.author==book_dto.author)
    if book_dto.publisher:
        query = query.where(Book.publisher.like(f'%{book_dto.publisher}%'))
    if book_dto.create_date:
        query = query.where(Book.create_date >= book_dto.create_date)
    result = await db.execute(query)
    return result.scalars().all()


@router.post('/book/insert')
async def insert_books(db: AsyncSession = Depends(create_session)):
    """插入5条测试数据"""
    books = [
        Book(book_name='西游记', author='吴承恩', publisher='人民文学出版社'),
        Book(book_name='红楼梦', author='曹雪芹', publisher='人民文学出版社'),
        Book(book_name='水浒传', author='施耐庵', publisher='人民文学出版社'),
        Book(book_name='三国演义', author='罗贯中', publisher='人民文学出版社'),
        Book(book_name='聊斋志异', author='蒲松龄', publisher='人民文学出版社'),
    ]
    db.add_all(books)
    await db.flush()
    return {"message": "插入成功", "count": len(books)}