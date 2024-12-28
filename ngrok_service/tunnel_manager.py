import logging
import requests
import time
from typing import Optional, Dict, Any
from pyngrok import ngrok
from pyngrok.conf import PyngrokConfig

class NgrokTunnelManager:
    def __init__(
        self,
        port: int = 9090,
        auth_token: Optional[str] = None,
        region: str = "us",
        max_retries: int = 10,
        retry_delay: int = 3
    ):
        """
        Initialize the NgrokTunnelManager.
        
        Args:
            port: The local port to tunnel
            auth_token: Ngrok auth token (optional)
            region: Ngrok region (default: "us")
            max_retries: Maximum number of connection retries
            retry_delay: Delay between retries in seconds
        """
        self.port = port
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.tunnel = None
        self.public_url = None
        
        if auth_token:
            ngrok.set_auth_token(auth_token)
        
        self.config = PyngrokConfig(region=region)
        self.logger = logging.getLogger(__name__)

    def start(self) -> str:
        """
        Start the ngrok tunnel.
        
        Returns:
            str: The public URL of the tunnel
        """
        try:
            self.tunnel = ngrok.connect(self.port, "http", pyngrok_config=self.config)
            self.public_url = self.tunnel.public_url
            self.logger.info(f"ngrok tunnel started on port {self.port}")
            self.logger.info(f"Public URL: {self.public_url}")
            return self.public_url
        except Exception as e:
            self.logger.error(f"Failed to start ngrok tunnel: {str(e)}")
            raise

    def wait_for_api(self) -> bool:
        """
        Wait for the ngrok API to become available.
        
        Returns:
            bool: True if API is available, False if max retries exceeded
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.get("http://localhost:4040/api/tunnels")
                if response.status_code == 200:
                    self.logger.info("ngrok API is available")
                    return True
            except requests.exceptions.ConnectionError:
                self.logger.info(f"ngrok API not available yet. Retrying in {self.retry_delay} seconds... (Attempt {attempt + 1}/{self.max_retries})")
                time.sleep(self.retry_delay)
        
        return False

    def get_tunnel_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the current tunnel.
        
        Returns:
            Optional[Dict[str, Any]]: Tunnel information or None if not available
        """
        try:
            response = requests.get("http://localhost:4040/api/tunnels")
            if response.status_code == 200:
                tunnels = response.json().get("tunnels", [])
                if tunnels:
                    return tunnels[0]
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get tunnel info: {str(e)}")
        
        return None

    def stop(self):
        """Stop the ngrok tunnel."""
        try:
            if self.tunnel:
                ngrok.disconnect(self.tunnel.public_url)
                self.logger.info("ngrok tunnel stopped")
                self.tunnel = None
                self.public_url = None
        except Exception as e:
            self.logger.error(f"Failed to stop ngrok tunnel: {str(e)}")
            raise

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
