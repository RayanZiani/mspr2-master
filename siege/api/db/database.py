from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.config import get_database_config

_database_url, _connect_args = get_database_config()

engine = create_async_engine(
    _database_url,
    echo=False,
    connect_args=_connect_args,
    # aiomysql/SQLAlchemy: pool_pre_ping déclenche un ping() incompatible (reconnect arg),
    # ce qui casse notamment /auth/login via une connexion poolée.
    pool_pre_ping=False,
    pool_recycle=3600,
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
