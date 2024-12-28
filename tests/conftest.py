import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
import json
from fastapi import FastAPI
from ngrok_service.router import router, lifespan

@pytest.fixture
def mock_ngrok_response():
    """Mock response for ngrok API calls"""
    return {
        "tunnels": [
            {
                "name": "test_tunnel",
                "uri": "/api/tunnels/test_tunnel",
                "public_url": "https://test.ngrok.io",
                "proto": "https",
                "config": {
                    "addr": "http://localhost:9090",
                    "inspect": True
                }
            }
        ]
    }

@pytest.fixture
def mock_requests_get(mock_ngrok_response):
    """Mock requests.get for ngrok API calls"""
    with patch('requests.get') as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_ngrok_response
        )
        yield mock_get

@pytest.fixture
def mock_requests_delete():
    """Mock requests.delete for ngrok API calls"""
    with patch('requests.delete') as mock_delete:
        mock_delete.return_value = MagicMock(status_code=204)
        yield mock_delete

@pytest.fixture
def mock_subprocess():
    """Mock subprocess for ngrok process management"""
    with patch('subprocess.Popen') as mock_popen:
        mock_popen.return_value = MagicMock(pid=12345)
        yield mock_popen

@pytest.fixture
def test_client():
    """Create a TestClient instance for FastAPI router testing"""
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)
    return TestClient(app)

@pytest.fixture(autouse=True)
def mock_env_vars():
    """Set environment variables for testing"""
    with patch.dict(os.environ, {
        'NGROK_AUTHTOKEN': 'test_token',
        'PORT': '9090'
    }):
        yield
