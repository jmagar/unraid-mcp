# Tech Context

## Technologies used

- Python (for the MCP server application)
- Docker (for containerization)
- `pip` (for Python package management)

## Development setup

- Current: Local Python development environment.
- Target: Dockerized application runnable in any Docker-compatible environment.

## Technical constraints

- The Docker container must successfully run the `unraid-mcp-server.py` script.
- All dependencies listed in `requirements.txt` must be installed in the Docker image.
- The container should be configurable via environment variables (e.g., for API keys, server address/port if applicable).
- The necessary network ports used by the MCP server must be exposed by the Docker container.
