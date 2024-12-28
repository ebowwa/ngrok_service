import pytest
from fastapi import FastAPI
from ngrok_service.router import router, ServerState, lifespan
import asyncio

@pytest.mark.asyncio
async def test_startup_event(mock_subprocess, mock_requests_get, mock_ngrok_response):
    """Test startup event handler"""
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)
    
    async with lifespan(app):
        # Verify ngrok was started
        mock_subprocess.assert_called_once()
        assert mock_subprocess.call_args[0][0] == ["ngrok", "http", "9090"]

@pytest.mark.asyncio
async def test_shutdown_event(mock_requests_get, mock_requests_delete, mock_ngrok_response):
    """Test shutdown event handler"""
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)
    
    async with lifespan(app):
        pass
    
    # Verify all tunnels were killed
    mock_requests_delete.assert_called_once_with(
        "http://localhost:4040/api/tunnels/test_tunnel"
    )

def test_get_server_info(test_client, mock_requests_get, mock_ngrok_response):
    """Test server info endpoint"""
    # Set the public URL directly for testing
    from ngrok_service.router import server_state
    server_state.public_url = "https://test.ngrok.io"
    
    response = test_client.get("/info")
    assert response.status_code == 200
    
    data = response.json()
    assert data["app_name"] == "Ngrok Service"
    assert data["port"] == 9090
    assert data["request_count"] == 1  # First request increments counter
    assert data["public_url"] == "https://test.ngrok.io"

def test_reset_request_count(test_client):
    """Test request counter reset endpoint"""
    # Make some requests to increment counter
    test_client.get("/info")
    test_client.get("/info")
    
    # Reset counter
    response = test_client.post("/reset-count")
    assert response.status_code == 200
    assert response.json()["message"] == "Request count reset to 0"
    
    # Verify counter was reset
    info_response = test_client.get("/info")
    assert info_response.json()["request_count"] == 1

@pytest.mark.asyncio
async def test_restart_ngrok(
    test_client,
    mock_subprocess,
    mock_requests_get,
    mock_requests_delete,
    mock_ngrok_response
):
    """Test ngrok restart endpoint"""
    response = test_client.post("/restart")
    assert response.status_code == 200
    
    data = response.json()
    assert data["message"] == "Ngrok restarted successfully"
    assert data["new_url"] == "https://test.ngrok.io"
    
    # Verify old tunnel was killed
    mock_requests_delete.assert_called_once()
    
    # Verify new tunnel was started
    mock_subprocess.assert_called_once()

@pytest.mark.asyncio
async def test_update_public_url_periodically(
    mock_requests_get,
    mock_ngrok_response
):
    """Test periodic URL update task"""
    state = ServerState()
    
    # Start update task
    task = asyncio.create_task(state.update_public_url())
    
    # Wait for one update
    await asyncio.sleep(1)
    
    # Cancel task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    
    # Verify URL was updated
    assert state.public_url == "https://test.ngrok.io"
    mock_requests_get.assert_called()
