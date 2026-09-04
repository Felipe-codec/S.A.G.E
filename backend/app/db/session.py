from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.logging import logger

engine_kwargs = {
    "pool_pre_ping": True,
}
if "sqlite" not in settings.DATABASE_URL:
    engine_kwargs.update({
        "pool_recycle": 300,
        "pool_size": 5,
        "max_overflow": 10,
        "connect_args": {"connect_timeout": 10},
    })

# Cria o engine SQLAlchemy com pool resiliente para ambientes cloud (Render/Supabase)
engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency do FastAPI para obter uma sessão de banco de dados por requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Verifica a saúde da conexão com o banco de dados (usado no endpoint /health/ready)."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Falha na checagem de prontidão do banco de dados: {e}")
        return False
