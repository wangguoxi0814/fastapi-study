from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import APIRouter, Depends

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
    create_date: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), default=func.now(), comment='创建时间')
    update_date: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), onupdate=func.now() ,default=func.now(), comment='更新时间')

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
    await create_tables()    # 启动时建表
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
        except:
            await session.rollback()
        finally:
            await session.close()

@router.get("/book/list")
async def book_list(db_session: AsyncSession = Depends(create_session)):
    print(f'db_session: {db_session}')
    result = await db_session.execute(select(Book))
    books = result.scalars().all()
    return books
