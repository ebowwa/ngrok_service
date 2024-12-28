import pytest
from unittest.mock import patch
from ngrok_service.utils import (
    check_ngrok_authtoken,
    list_active_tunnels,
    get_ngrok_url_for_port,
    get_all_ngrok_urls,
    kill_active_tunnel,
    kill_all_tunnels
)
import requests

def test_check_ngrok_authtoken_success(mock_env_vars):
    """Test successful authtoken retrieval"""
    token = check_ngrok_authtoken()
    assert token == 'test_token'

def test_check_ngrok_authtoken_missing():
    """Test missing authtoken handling"""
    with pytest.raises(ValueError) as exc_info:
        with patch.dict('os.environ', {}, clear=True):
            check_ngrok_authtoken()
    assert str(exc_info.value) == "NGROK_AUTHTOKEN is not set in environment variables."

def test_list_active_tunnels_success(mock_requests_get, mock_ngrok_response):
    """Test successful tunnel listing"""
    tunnels = list_active_tunnels()
    assert tunnels == mock_ngrok_response['tunnels']
    mock_requests_get.assert_called_once_with("http://localhost:4040/api/tunnels")

def test_list_active_tunnels_failure(mock_requests_get):
    """Test tunnel listing failure handling"""
    mock_requests_get.side_effect = requests.exceptions.RequestException()
    tunnels = list_active_tunnels()
    assert tunnels == []

def test_get_ngrok_url_for_port_success(mock_requests_get, mock_ngrok_response):
    """Test successful URL retrieval for port"""
    url = get_ngrok_url_for_port(9090)
    assert url == "https://test.ngrok.io"

def test_get_ngrok_url_for_port_not_found(mock_requests_get, mock_ngrok_response):
    """Test URL retrieval for non-existent port"""
    url = get_ngrok_url_for_port(8080)
    assert url is None

def test_get_all_ngrok_urls_success(mock_requests_get, mock_ngrok_response):
    """Test successful retrieval of all URLs"""
    urls = get_all_ngrok_urls()
    assert urls == ["https://test.ngrok.io"]

def test_kill_active_tunnel_success(mock_requests_delete):
    """Test successful tunnel termination"""
    result = kill_active_tunnel("test_tunnel")
    assert result is True
    mock_requests_delete.assert_called_once_with(
        "http://localhost:4040/api/tunnels/test_tunnel"
    )

def test_kill_active_tunnel_failure(mock_requests_delete):
    """Test tunnel termination failure handling"""
    mock_requests_delete.side_effect = requests.exceptions.RequestException()
    result = kill_active_tunnel("test_tunnel")
    assert result is False

def test_kill_all_tunnels(mock_requests_get, mock_requests_delete, mock_ngrok_response):
    """Test killing all active tunnels"""
    kill_all_tunnels()
    mock_requests_delete.assert_called_once_with(
        "http://localhost:4040/api/tunnels/test_tunnel"
    )
