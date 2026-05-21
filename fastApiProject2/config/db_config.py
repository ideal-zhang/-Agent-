from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession


ASYNC_DATABASE_URL = "mysql+aiomysql://root:261224@localhost:3306/news_app?charset=utf8mb4"
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True, #输出sql日志
    pool_size = 10, # 设置连接池的活跃连接数
    max_overflow = 20, # 运行额外的连接数
)

AsyncSessionLocal = async_sessionmaker(
    bind = async_engine,     # 绑定数据库引擎
    class_=AsyncSession,     # 指定会话类
    expire_on_commit = False # 提交后会话不过期，不会重新查询数据库
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()