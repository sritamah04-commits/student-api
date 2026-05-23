import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import Student

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args = {"check_same_thread": False}


)
TestingSessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
app.dependency_overrides[get_db] = override_get_db

Student.__table__.schema = None

@pytest.fixture(scope = "module")
def setup_database():
    Base.metadata.create_all(bind = engine)
    yield
    Base.metadata.drop_all(bind = engine)

@pytest.fixture(scope = "module")
def client(setup_database):
    return TestClient(app)

@pytest.fixture(scope = "module")
def auth_token(client):
    response = client.post(
        "/login",
        data={"username": "admin", "password": "secret123"}
    )
    return response.json()["access_token"]

@pytest.fixture(autouse = True)
def clean_db():
    db = TestingSessionLocal()
    db.query(Student).delete()
    db.commit()
    db.close()

@pytest.fixture
def sample_student(client, auth_token):
    response = client.post(
        "/students/",
        json = {
            "name" : "sritama Hazra",
            "email" : "sri1234@gmail.com",
            "age" : 21,
            "gpa" : 8,
            "course" : "AIML"
        },
        headers = {"Authorization" : f"Bearer {auth_token}"}
    )
    return response.json()
    
        
