from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Determine the async database URL
db_url = settings.DATABASE_URL

# If using PostgreSQL with standard URL, convert to async
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
async_engine = create_async_engine(db_url, echo=settings.DEBUG)

# Session factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables created")


# Optional SATA database connection
sata_engine = None
SataSessionLocal = None

if settings.SATA_DATABASE_URL:
    try:
        sata_url = settings.SATA_DATABASE_URL
        if sata_url.startswith("postgresql://"):
            sata_url = sata_url.replace("postgresql://", "postgresql+asyncpg://")
        
        sata_engine = create_async_engine(sata_url, echo=settings.DEBUG)
        SataSessionLocal = sessionmaker(
            bind=sata_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    except Exception as e:
        logger.warning(f"⚠️ SATA database not available: {e}")


async def get_sata_db():
    """Dependency to get SATA database session."""
    if not SataSessionLocal:
        raise Exception("SATA database not configured")
    async with SataSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
