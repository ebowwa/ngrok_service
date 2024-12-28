# Ngrok Service

A Python package for managing ngrok tunnels with enhanced error handling and monitoring capabilities.

## Features

- Easy tunnel management with context manager support
- Configurable retry mechanism for API availability
- Detailed logging and error handling
- Tunnel information retrieval
- Support for authentication and region configuration

## Installation

```bash
pip install -e .
```

## Usage

```python
from ngrok_service import NgrokTunnelManager

# Basic usage
manager = NgrokTunnelManager(port=9090)
public_url = manager.start()
print(f"Tunnel available at: {public_url}")

# Using context manager
with NgrokTunnelManager(port=9090) as tunnel:
    print(f"Tunnel available at: {tunnel.public_url}")
    # Your application code here

# With authentication
manager = NgrokTunnelManager(
    port=9090,
    auth_token="your_auth_token",
    region="us"
)

# Get tunnel information
tunnel_info = manager.get_tunnel_info()
print(tunnel_info)
```

## Configuration

- `port`: Local port to tunnel (default: 9090)
- `auth_token`: Ngrok authentication token (optional)
- `region`: Ngrok region (default: "us")
- `max_retries`: Maximum number of connection retries (default: 10)
- `retry_delay`: Delay between retries in seconds (default: 3)

## Error Handling

The package includes comprehensive error handling for common scenarios:
- Connection failures
- API availability issues
- Authentication errors
- Tunnel management errors

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
