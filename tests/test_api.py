import torch
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    # Using 'with' triggers the app lifespan (startup/shutdown events)
    with TestClient(app) as c:
        yield c

def test_root(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_search_valid(client):
    """Test standard semantic search query."""
    payload = {"query": "Which Ford SUV has 7 seats?"}
    response = client.post("/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0 # Should return top_k results
    assert "content" in data[0]
    assert "score" in data[0]

def test_search_invalid_empty(client):
    """Test search with empty query triggers Pydantic validation."""
    payload = {"query": ""}
    response = client.post("/search", json=payload)
    assert response.status_code == 422

def test_recommend_valid(client):
    """Test recommendation engine with towing intent."""
    payload = {"needs": "I want a pickup truck for towing"}
    response = client.post("/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) > 0
    assert "model" in data["recommendations"][0]

def test_recommend_family(client):
    """Test recommendation engine for family usage intent."""
    payload = {"needs": "I need a family SUV"}
    response = client.post("/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["recommendations"]) > 0

def test_recommend_invalid_empty(client):
    """Test recommendation with empty constraints."""
    payload = {"needs": ""}
    response = client.post("/recommend", json=payload)
    assert response.status_code == 422

def test_ask_valid(client):
    """Test RAG capabilities based on engine lights."""
    payload = {"question": "What does engine warning light mean?"}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 10 # Meaningful response
    assert "context_used" in data
    assert isinstance(data["context_used"], list)

def test_ask_invalid_empty(client):
    """Test RAG assistant catching empty questions."""
    payload = {"question": ""}
    response = client.post("/ask", json=payload)
    assert response.status_code == 422

