import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.config import TEST_DATABASE_URL
from app.cache import redis_client


engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    database = TestingSessionLocal()

    try:
        yield database
    finally:
        database.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    try:
        redis_client.flushdb()
    except Exception:
        pass

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def user_data():
    return {
        "name": "Rituraj",
        "email": "rituraj@gmail.com",
        "password": "123456"
    }


@pytest.fixture
def second_user_data():
    return {
        "name": "Aman",
        "email": "aman@gmail.com",
        "password": "123456"
    }


@pytest.fixture
def third_user_data():
    return {
        "name": "Rahul",
        "email": "rahul@gmail.com",
        "password": "123456"
    }


def register_user(client, user):
    return client.post("/auth/register", json=user)


def login_user(client, email, password):
    return client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )


def get_auth_headers(client, user):
    register_user(client, user)

    response = login_user(
        client,
        user["email"],
        user["password"]
    )

    access_token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}"
    }


@pytest.fixture
def auth_headers(client, user_data):
    return get_auth_headers(client, user_data)


@pytest.fixture
def second_auth_headers(client, second_user_data):
    return get_auth_headers(client, second_user_data)


@pytest.fixture
def third_auth_headers(client, third_user_data):
    return get_auth_headers(client, third_user_data)
