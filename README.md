# Unraid MCP Server

This server provides an MCP interface to interact with an Unraid server's GraphQL API.

## Setup

This section describes the setup for local development **without Docker**. For Docker-based deployment, see the "Docker" section below.

1.  Ensure your main project dependencies (including `fastmcp`, `python-dotenv`, `httpx`) are installed. If your project uses `pyproject.toml`, this is typically done via a command like `uv pip install -e .` or `pip install -e .` from the project root.
2.  Navigate to the directory containing `unraid-mcp-server.py` (e.g., `src/unraid-mcp/` or the project root if it's there).
3.  Copy `.env.example` to `.env`: `cp .env.example .env`
4.  Edit `.env` and fill in your Unraid and MCP server details:
    *   `UNRAID_API_URL`: Your Unraid GraphQL endpoint (e.g., `http://your-unraid-ip/graphql`). **Required.**
    *   `UNRAID_API_KEY`: Your Unraid API key. **Required.**
    *   `UNRAID_MCP_TRANSPORT` (optional, defaults to `sse` for local non-Docker. `streamable-http` is recommended for new setups). Valid options: `streamable-http`, `sse`, `stdio`.
    *   `UNRAID_MCP_HOST` (optional, defaults to `0.0.0.0` for network transports, listens on all interfaces).
    *   `UNRAID_MCP_PORT` (optional, defaults to `6970` for network transports).
    *   `UNRAID_MCP_LOG_LEVEL` (optional, defaults to `INFO`). Examples: `DEBUG`, `INFO`, `WARNING`, `ERROR`.
    *   `UNRAID_MCP_LOG_FILE` (optional, defaults to `unraid-mcp.log` in the script's directory).
    *   `UNRAID_VERIFY_SSL` (optional, defaults to `true`. Set to `false` for self-signed certificates, or provide a path to a CA bundle).

## Running the Server

From the project root (`yarr-mcp/`):

```bash
python src/unraid-mcp/unraid-mcp-server.py
```

Or from `src/unraid-mcp/`:

```bash
python unraid-mcp-server.py
```

The server will start, by default using SSE transport on port 6970.

## Implemented Tools

Below is a list of the implemented tools and their basic functions. 
Refer to the Unraid GraphQL schema for detailed response structures.

*   `get_system_info()`: Retrieves comprehensive system, OS, CPU, memory, and hardware information.
*   `get_array_status()`: Gets the current status of the storage array, capacity, and disk details.
*   `list_docker_containers(skip_cache: Optional[bool] = False)`: Lists all Docker containers.
*   `manage_docker_container(container_id: str, action: str)`: Starts or stops a Docker container (action: "start" or "stop").
*   `get_docker_container_details(container_identifier: str)`: Gets detailed info for a specific Docker container by ID or name.
*   `list_vms()`: Lists all Virtual Machines and their states.
*   `manage_vm(vm_id: str, action: str)`: Manages a VM (actions: "start", "stop", "pause", "resume", "forceStop", "reboot").
*   `get_vm_details(vm_identifier: str)`: Gets details for a specific VM by ID or name.
*   `get_shares_info()`: Retrieves information about all user shares.
*   `get_notifications_overview()`: Gets an overview of system notifications (counts by severity/status).
*   `list_notifications(type: str, offset: int, limit: int, importance: Optional[str] = None)`: Lists notifications with filters.
*   `list_available_log_files()`: Lists all available log files.
*   `get_logs(log_file_path: str, tail_lines: Optional[int] = 100)`: Retrieves content from a specific log file (tails last N lines).
*   `list_physical_disks()`: Lists all physical disks recognized by the system.
*   `get_disk_details(disk_id: str)`: Retrieves detailed SMART info and partition data for a specific physical disk.
*   `get_unraid_variables()`: Retrieves a wide range of Unraid system variables and settings.
*   `get_network_config()`: Retrieves network configuration details, including access URLs.
*   `get_registration_info()`: Retrieves Unraid registration details.
*   `get_connect_settings()`: Retrieves settings related to Unraid Connect.

### Claude Desktop Client Configuration

If your Unraid MCP Server is running on `localhost:6970` (the default for SSE):

Create or update your Claude Desktop MCP settings file at `~/.config/claude/claude_mcp_settings.jsonc` (create the `claude` directory if it doesn't exist).
Add or update the entry for this server:

```jsonc
{
  "mcp_servers": {
    "unraid": { // Use a short, descriptive name for the client
      "url": "http://localhost:6970/mcp", // Default path for FastMCP SSE is /mcp
      "disabled": false,
      "timeout": 60, // Optional: timeout in seconds for requests
      "transport": "sse" // Explicitly set transport if not default or for clarity
    }
    // ... other server configurations
  }
}
```

Make sure the `url` matches your `UNRAID_MCP_HOST` and `UNRAID_MCP_PORT` settings if you've changed them from the defaults.

(Details to be added after implementation based on the approved toolset.)

## Docker

This application can be containerized using Docker.

### Prerequisites

*   Docker installed and running.

### Building the Image

1.  Navigate to the root directory of this project (`unraid-mcp`).
2.  Build the Docker image:

    ```bash
    docker build -t unraid-mcp-server .
    ```

### Running the Container

To run the container, you'll need to provide the necessary environment variables. You can do this directly on the command line or by using an environment file.

**Option 1: Using an environment file (recommended)**

1.  Create a file named `.env.local` in the project root (this file is in `.dockerignore` and won't be copied into the image).
2.  Add your environment variables to `.env.local`:

    ```env
    UNRAID_API_URL=http://your-unraid-ip/graphql
    UNRAID_API_KEY=your-unraid-api-key
    # Optional: override default port
    # UNRAID_MCP_PORT=6971 
    # Optional: override log level
    # UNRAID_MCP_LOG_LEVEL=DEBUG
    # Optional: SSL verification settings
    # UNRAID_VERIFY_SSL=false
    ```

3.  Run the container, mounting the `.env.local` file:

    ```bash
    docker run -d --name unraid-mcp --restart unless-stopped -p 6970:6970 --env-file .env.local unraid-mcp-server
    ```
    *   `-d`: Run in detached mode.
    *   `--name unraid-mcp`: Assign a name to the container.
    *   `--restart unless-stopped`: Restart policy.
    *   `-p 6970:6970`: Map port 6970 on the host to port 6970 in the container. Adjust if you changed `UNRAID_MCP_PORT`.
    *   `--env-file .env.local`: Load environment variables from the specified file.

**Option 2: Providing environment variables directly**

```bash
docker run -d --name unraid-mcp --restart unless-stopped -p 6970:6970 \
  -e UNRAID_API_URL="http://your-unraid-ip/graphql" \
  -e UNRAID_API_KEY="your-unraid-api-key" \
  unraid-mcp-server
```

### Accessing Logs

To view the logs of the running container:

```bash
docker logs unraid-mcp
```

Follow logs in real-time:

```bash
docker logs -f unraid-mcp
```

### Stopping and Removing the Container

(Using `docker run` commands)

```bash
docker stop unraid-mcp
docker rm unraid-mcp
```

### Using Docker Compose

A `docker-compose.yml` file is provided for easier management.

**Prerequisites:**

*   Docker Compose installed (usually included with Docker Desktop).
*   Ensure you have an `.env.local` file in the same directory as `docker-compose.yml` with your `UNRAID_API_URL` and `UNRAID_API_KEY` (and any other overrides). See "Option 1: Using an environment file" in the `docker run` section above for an example `.env.local` content.
*   If you haven't built the image yet, Docker Compose can build it for you if you uncomment the `build` section in `docker-compose.yml` or build it manually first: `docker build -t unraid-mcp-server .`

**Starting the service:**

```bash
docker-compose up -d
```

This will start the `unraid-mcp` service in detached mode.

**Viewing logs:**

```bash
docker-compose logs -f unraid-mcp
```

**Stopping the service:**

```bash
docker-compose down
```

This stops and removes the container defined in the `docker-compose.yml` file.

### Claude Desktop Client Configuration (for Docker)

```bash
docker stop unraid-mcp
docker rm unraid-mcp
```

### Claude Desktop Client Configuration (for Docker)

If your Unraid MCP Server is running in Docker and exposed on `localhost:6970` (default Docker setup):

Create or update your Claude Desktop MCP settings file at `~/.config/claude/claude_mcp_settings.jsonc`.
Add or update the entry for this server:

```jsonc
{
  "mcp_servers": {
    "unraid": { // Use a short, descriptive name for the client
      "url": "http://localhost:6970/mcp", // Default path for FastMCP streamable-http is /mcp
      "disabled": false,
      "timeout": 60, // Optional: timeout in seconds for requests
      "transport": "streamable-http" // Ensure this matches the server's transport
    }
    // ... other server configurations
  }
}
```
Make sure the `url` (host and port) matches your Docker port mapping. The default transport in the Dockerfile is `streamable-http`. # unraid-mcp
