from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import asyncio
import os
import sys
from typing import Optional
from contextlib import asynccontextmanager
from .utils import (
    get_ngrok_url_for_port,
    kill_all_tunnels,
    list_active_tunnels
)

router = APIRouter(tags=["ngrok"])

class ServerState:
    def __init__(self):
        self.request_count: int = 0
        self.port: int = int(os.getenv("PORT", 9090))
        self.public_url: Optional[str] = None
        self._update_task: Optional[asyncio.Task] = None

    async def update_public_url(self):
        """Update the public URL periodically."""
        while True:
            try:
                url = get_ngrok_url_for_port(self.port)
                if url and url != self.public_url:
                    self.public_url = url
                    print(f"Updated public URL: {url}")
            except Exception as e:
                print(f"Error updating public URL: {e}", file=sys.stderr)
            await asyncio.sleep(60)

server_state = ServerState()

async def increment_request_count():
    """Dependency to increment the request count."""
    server_state.request_count += 1

@asynccontextmanager
async def lifespan(app):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    port = os.getenv("PORT")
    if port:
        try:
            server_state.port = int(port)
        except ValueError:
            print(f"Invalid PORT environment variable: {port} # index.py server port. Using default port {server_state.port}.")
    
    if not server_state.public_url:
        start_ngrok(server_state.port)
    
    # Start URL update task
    server_state._update_task = asyncio.create_task(server_state.update_public_url())
    
    yield
    
    # Shutdown
    if server_state._update_task:
        server_state._update_task.cancel()
    kill_all_tunnels()

def start_ngrok(port: int) -> None:
    """Start ngrok tunnel for the specified port."""
    try:
        import subprocess
        subprocess.Popen(
            ["ngrok", "http", str(port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"ngrok started on port {port}")
    except FileNotFoundError:
        print("ngrok executable not found. Please ensure ngrok is installed and in your PATH.", file=sys.stderr)
    except Exception as e:
        print(f"Failed to start ngrok: {e}", file=sys.stderr)

@router.get("/info")
async def get_server_info(increment: bool = Depends(increment_request_count)):
    """Get current server information."""
    return JSONResponse({
        "app_name": "Ngrok Service",
        "port": server_state.port,
        "public_url": server_state.public_url,
        "request_count": server_state.request_count
    })

@router.post("/reset-count")
async def reset_request_count():
    """Reset the request counter to zero."""
    server_state.request_count = 0
    return JSONResponse({"message": "Request count reset to 0"})

@router.post("/restart")
async def restart_ngrok():
    """Restart ngrok to obtain a new public URL."""
    try:
        kill_all_tunnels()
        start_ngrok(server_state.port)
        
        # Wait for the new tunnel
        for _ in range(10):
            await asyncio.sleep(3)
            new_url = get_ngrok_url_for_port(server_state.port)
            if new_url:
                server_state.public_url = new_url
                return JSONResponse({
                    "message": "Ngrok restarted successfully",
                    "new_url": new_url
                })
        
        raise HTTPException(
            status_code=500,
            detail="Failed to obtain new ngrok URL after restart"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to restart ngrok: {str(e)}"
        )
