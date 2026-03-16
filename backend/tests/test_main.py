import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app, get_db

# 1. Setup the TestClient
client = TestClient(app)

# 2. Test the Health Check
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "Smart Semantic Search" in response.json().get("message", "")

# 3. The "Fix Everything" Test
@patch("main.get_embedding")
def test_search_endpoint(mock_embedding):
    # Setup A: Mock the AI vector return (Prevents real API call)
    mock_embedding.return_value = [0.1] * 3072
    
    # Setup B: Create a fake Product result (Simulates DB data)
    mock_product = MagicMock()
    mock_product.id = 1
    mock_product.name = "Test Laptop"
    mock_product.description = "A high-performance laptop."

    # Setup C: Dependency Override (The Secret Sauce)
    # This replaces the real 'get_db' with a fake one that returns a Mock Session
    mock_session = MagicMock()
    
    def override_get_db():
        try:
            yield mock_session # Injects our mock instead of a real SQLite/Postgres session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db #

    # Setup D: Tell the Mock Session what to return when queried
    # chain: db.query().order_by().limit().all()
    mock_query = mock_session.query.return_value
    mock_query.order_by.return_value.limit.return_value.all.return_value = [mock_product]
    
    # Act
    try:
        response = client.get("/search?query=laptop")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data[0]["name"] == "Test Laptop"
    finally:
        # ALWAYS clear overrides after the test so they don't leak into other tests
        app.dependency_overrides.clear() #