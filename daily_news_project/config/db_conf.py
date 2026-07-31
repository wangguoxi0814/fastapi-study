from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

ASYNC_DATABASE_URL = "mysql+aiomysql://root:root@localhost:3306/news_app?charset=utf8mb4"

# 创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,  # 可选：输出SQL日志
    pool_size=10,  # 设置连接池中保持的持久连接数
    max_overflow=20  # 设置连接池允许创建的额外连接数
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as db_session:
        try:
            yield db_session
            await db_session.commit()
        except Exception as e:
            await db_session.rollback()
            raise e
        finally:
            await db_session.close()