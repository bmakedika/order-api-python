import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.core.auth import require_admin, require_user
from app.core.redis_client import get_redis


# DB SQLite in momory for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# override get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# override auth dependencies

def override_require_admin():
    return {"sub": "admin@example.com", "role": "admin"}

def override_require_user():
    return {"sub": "user@example.com", "role": "user"}

# pytest fixture for client

@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    get_redis().flushdb()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides = {}

@pytest.fixture(scope="function")
def client_auth():
    Base.metadata.create_all(bind=engine)
    get_redis().flushdb()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_admin] = override_require_admin
    app.dependency_overrides[require_user] = override_require_user

    yield TestClient(app)

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides = {}