from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr

from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine: AsyncEngine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def get_db():
    async with SessionLocal() as session:
        yield session


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    id: Mapped[int] = mapped_column(primary_key=True)
