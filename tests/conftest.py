import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.core.auth import require_admin, require_user


# DB SQLite in momory for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# override get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# override auth dependencies
def override_require_admin():
    return {'sub': 'admin', 'role': 'admin'}

def override_require_user():
    return {'sub': 'user', 'role': 'user'}


@pytest.fixture(scope='function')
def client():
    # create tables
    Base.metadata.create_all(bind=engine)

    # override dependencies
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_admin] = override_require_admin
    app.dependency_overrides[require_user] = override_require_user

    yield TestClient(app)


    # Clean up DB after test
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides = {}