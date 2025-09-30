# backend/product_service/app/db.py
import logging
import os

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()

def _build_primary_url() -> str:
    # Highest priority: explicit URL
    explicit = os.getenv("DATABASE_URL")
    if explicit:
        return explicit

    # Use SQLite automatically when running tests/CI unless DATABASE_URL was set
    if os.getenv("TESTING") == "1" or os.getenv("PYTEST_CURRENT_TEST"):
        # File-based SQLite works well with SQLAlchemy's create/drop in tests
        return "sqlite:///./products_test.db"

    # Otherwise, construct a Postgres URL (default host -> localhost, not 'postgres')
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = (
        os.getenv("POSTGRES_HOST")
        or os.getenv("DB_HOST")
        or "localhost"  # <- IMPORTANT: avoid defaulting to 'postgres'
    )
    port = os.getenv("POSTGRES_PORT") or os.getenv("DB_PORT") or "5432"
    db = os.getenv("POSTGRES_DB") or os.getenv("DB_NAME") or "products"
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


def _create_engine_with_fallback():
    primary_url = _build_primary_url()

    # Engine kwargs per driver
    if primary_url.startswith("postgresql"):
        engine = create_engine(
            primary_url,
            future=True,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 5},
        )
    else:
        engine = create_engine(
            primary_url,
            future=True,
            connect_args={"check_same_thread": False},
        )

    # Validate connectivity early so tests can fall back cleanly
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Product Service DB: using %s", primary_url)
        return engine
    except Exception as e:
        # Fallback to SQLite if Postgres is unreachable in CI
        fallback_url = "sqlite:///./products_fallback.db"
        logger.warning(
            "Product Service DB: failed to connect to primary DB (%s): %s. "
            "Falling back to SQLite at %s",
            primary_url,
            e,
            fallback_url,
        )
        return create_engine(
            fallback_url,
            future=True,
            connect_args={"check_same_thread": False},
        )

# The engine the rest of the app/tests import
engine = _create_engine_with_fallback()

# Session factory and dependency
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
