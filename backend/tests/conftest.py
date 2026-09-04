import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Garante inclusão do diretório backend no path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Configura variáveis de ambiente para testes
os.environ["APP_ENV"] = "test"
os.environ["JWT_SECRET"] = "test-jwt-secret-key-very-long-min-32-chars"
os.environ["MASTER_ENCRYPTION_KEY"] = "VZaokCbhHYZg5M6sslHozPjTZijU5bGgm74kVXE7JB8="
os.environ["CORS_ORIGINS"] = "http://localhost:5173"
os.environ["FRONTEND_URL"] = "http://localhost:5173"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.db.base import Base
from app.db.session import get_db
from app.main import app

# Engine SQLite em memória para execução de testes unitários isolados
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
