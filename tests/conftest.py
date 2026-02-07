import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apps.config.database import Base, get_db
from main import app

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client):
    """Create an admin user and return auth token"""
    # Register admin
    response = client.post(
        "/api/v1/users/register",
        json={
            "name": "Admin User",
            "email": "admin@test.com",
            "password": "Password@123",
            "role": "admin"
        }
    )
    assert response.status_code == 201
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "Password@123"}
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


@pytest.fixture
def student_token(client):
    """Create a student user and return auth token"""
    # Register student
    response = client.post(
        "/api/v1/users/register",
        json={
            "name": "Student User",
            "email": "student@test.com",
            "password": "Password@123",
            "role": "student"
        }
    )
    assert response.status_code == 201
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "student@test.com", "password": "Password@123"}
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


@pytest.fixture
def sample_course(client, admin_token):
    """Create a sample course"""
    response = client.post(
        "/api/v1/courses",
        json={
            "title": "Introduction to Python",
            "code": "PY101",
            "capacity": 30
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    return response.json()["data"]
