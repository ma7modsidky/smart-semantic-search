import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

# 1. Test the Health Check (Simple)
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "Smart Semantic Search" in response.json().get("message", "")

# 2. Test the Search Endpoint (Mocking the AI)
@patch("main.get_embedding") # This prevents the real AI call
def test_search_endpoint(mock_embedding):
    # Setup: Tell the mock to return a fake 3072-dim vector
    mock_embedding.return_value = [0.1] * 3072
    
    # Act: Call your search endpoint
    response = client.get("/search?query=laptop")
    
    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # Ensure it's returning the Pydantic schema (no embedding field)
    if len(response.json()) > 0:
        assert "embedding" not in response.json()[0]
        assert "name" in response.json()[0]