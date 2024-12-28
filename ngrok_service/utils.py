import os
import subprocess
import threading
import time
import re
import logging
import requests
from typing import Optional, List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_ngrok_authtoken() -> str:
    """
    Ensures that the NGROK_AUTHTOKEN is available in the environment.
    Raises an error if not set.
    """
    authtoken = os.getenv("NGROK_AUTHTOKEN")
    if not authtoken:
        raise ValueError("NGROK_AUTHTOKEN is not set in environment variables.")
    return authtoken

def list_active_tunnels() -> List[Dict[str, Any]]:
    """
    Retrieves a list of all active Ngrok tunnels by querying the Ngrok local API.
    
    Returns:
        list: A list of dictionaries containing tunnel details.
    """
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        response.raise_for_status()
        data = response.json()
        return data.get("tunnels", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Ngrok tunnels: {e}")
        return []

def get_ngrok_url_for_port(port: int) -> Optional[str]:
    """
    Retrieves the public URL of the Ngrok tunnel running on the specified port.
    
    Args:
        port: The local port number to check.
    
    Returns:
        The public URL if found, else None.
    """
    tunnels = list_active_tunnels()
    for tunnel in tunnels:
        addr = tunnel.get("config", {}).get("addr", "")
        match = re.search(r":(\d+)$", addr)
        if match and int(match.group(1)) == port:
            return tunnel.get("public_url")
    return None

def get_all_ngrok_urls() -> List[str]:
    """
    Retrieves all active Ngrok public URLs.
    
    Returns:
        A list of public URLs.
    """
    tunnels = list_active_tunnels()
    return [tunnel.get("public_url") for tunnel in tunnels if tunnel.get("public_url")]

def kill_active_tunnel(tunnel_name: str) -> bool:
    """
    Terminates a specific Ngrok tunnel by its tunnel name using the Ngrok local API.
    
    Args:
        tunnel_name: The name of the tunnel to terminate.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        requests.delete(f"http://localhost:4040/api/tunnels/{tunnel_name}")
        return True
    except requests.exceptions.RequestException:
        return False

def kill_all_tunnels() -> None:
    """
    Terminates all active Ngrok tunnels by querying the Ngrok local API.
    """
    tunnels = list_active_tunnels()
    for tunnel in tunnels:
        name = tunnel.get("name")
        if name:
            kill_active_tunnel(name)
    logger.info("All Ngrok tunnels have been terminated.")
