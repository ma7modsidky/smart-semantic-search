import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

# 1. The Monkeypatch: This runs BEFORE the TestClient or App starts
@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """
    Forcibly sets environment variables for the duration of the test.
    This prevents the app from trying to connect to the real 'db' host.
    """
    monkeypatch.setenv("AI_API_KEY", "test_dummy_key")

client = TestClient(app)

# 2. Test the Health Check
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "Smart Semantic Search" in response.json().get("message", "")

# 3. Test the Search Endpoint
@patch("main.get_embedding")
def test_search_endpoint(mock_embedding):
    # Setup A: Mock the AI vector return
    mock_embedding.return_value = [0.1] * 3072
    
    # Setup B: Create a fake Product object
    mock_product = MagicMock()
    mock_product.id = 1
    mock_product.name = "Test Laptop"
    mock_product.description = "A high-performance laptop."

    # Setup C: Mock the Database Dependency
    # We patch 'get_db' because your refined main.py uses 'Depends(get_db)'
    with patch("main.get_db") as mock_get_db:
        mock_db_session = MagicMock()
        # Mock the dependency yield behavior
        mock_get_db.return_value = iter([mock_db_session]) 
        
        # Mock the SQLAlchemy query chain
        mock_query = mock_db_session.query.return_value
        mock_query.order_by.return_value.limit.return_value.all.return_value = [mock_product]
        
        # Act
        response = client.get("/search?query=laptop")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data[0]["name"] == "Test Laptop"
        assert "embedding" not in data[0] # Verify Pydantic filters the vector