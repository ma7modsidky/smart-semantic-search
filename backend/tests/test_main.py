import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app, ProductResponse

client = TestClient(app)

# 1. Test the Health Check
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "Smart Semantic Search" in response.json().get("message", "")

# 2. Test the Search Endpoint (Double Mock Strategy)
@patch("main.get_embedding")
@patch("main.Session") # Mock the Database Session
def test_search_endpoint(mock_db_session, mock_embedding):
    # Setup A: Mock the AI vector
    mock_embedding.return_value = [0.1] * 3072
    
    # Setup B: Create a fake Product object that looks like a database result
    mock_product = MagicMock()
    mock_product.id = 1
    mock_product.name = "Test Laptop"
    mock_product.description = "A high-performance laptop."
    # Note: We don't even need to give it an embedding because 
    # the ProductResponse schema filters it out anyway.

    # Setup C: Mock the SQLAlchemy chain: db.query().order_by().limit().all()
    mock_query = mock_db_session.return_value.query.return_value
    mock_query.order_by.return_value.limit.return_value.all.return_value = [mock_product]
    
    # Act
    response = client.get("/search?query=laptop")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["name"] == "Test Laptop"
    assert "embedding" not in data[0] # Confirms Pydantic is working