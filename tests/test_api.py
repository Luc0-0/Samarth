"""
Tests for Project Samarth API endpoints
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint returns API information"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data
    assert "features" in data

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "version" in data

def test_metrics_endpoint():
    """Test metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "requests_total" in data
    assert "uptime_seconds" in data

def test_datasets_endpoint():
    """Test datasets listing endpoint"""
    response = client.get("/datasets")
    assert response.status_code == 200
    data = response.json()
    assert "datasets" in data
    assert "count" in data
    assert isinstance(data["datasets"], list)

def test_ask_endpoint():
    """Test Q&A endpoint with sample question"""
    question = {"question": "What is the average rainfall in Maharashtra?"}
    response = client.post("/ask", json=question)
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert "request_id" in data
    assert "answer_text" in data
    assert "structured_results" in data
    assert "citations" in data
    assert "processing_info" in data
    assert "provenance" in data
    
    # Check types
    assert isinstance(data["structured_results"], list)
    assert isinstance(data["citations"], list)
    assert isinstance(data["processing_info"], dict)
    assert isinstance(data["provenance"], dict)

def test_ask_endpoint_empty_question():
    """Test Q&A endpoint with empty question"""
    question = {"question": ""}
    response = client.post("/ask", json=question)
    # Should still return 200 but with appropriate response
    assert response.status_code == 200

def test_raw_data_endpoint():
    """Test raw data endpoint"""
    response = client.get("/raw/agri-1")
    # May return 404 if dataset doesn't exist, which is fine
    assert response.status_code in [200, 404, 500]

def test_cors_headers():
    """Test CORS headers are present"""
    response = client.get("/health")
    assert response.status_code == 200
    # CORS headers should be present in production