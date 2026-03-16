import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app, get_db
from models import Base, Product

# 1. Setup an In-Memory SQLite Database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://" #

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. Dependency override: Tell FastAPI to use our test DB
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db #

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Create tables and a dummy product before each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Add one dummy product so the search has something to find
    dummy_product = Product(
        name="Test Laptop",
        description="A high-performance laptop for testing.",
        embedding=[0.1] * 3072
    )
    db.add(dummy_product)
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

# --- Tests ---

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "Smart Semantic Search" in response.json().get("message", "")

@patch("main.get_embedding")
def test_search_endpoint(mock_embedding):
    # Setup: Mock the AI to return a vector matching our dummy product
    mock_embedding.return_value = [0.1] * 3072
    
    # Act
    response = client.get("/search?query=laptop")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == "Test Laptop"
    assert "embedding" not in data[0] # Verify Pydantic schema