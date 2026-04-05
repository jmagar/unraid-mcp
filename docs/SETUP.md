# Setup Guide -- unraid-mcp

Step-by-step instructions to get unraid-mcp running locally, in Docker, or as a Claude Code plugin.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- An Unraid server with the API enabled (Settings > Management Access > API Keys)
- Docker and Docker Compose (for container deployment)

## Option 1: Interactive setup (recommended)

The server includes an elicitation-based setup wizard that collects credentials interactively.

1. Install as a Claude Code plugin:
   ```bash
   /plugin marketplace add jmagar/claude-homelab
   /plugin install unraid-mcp @jmagar-claude-homelab
   ```

2. Run the setup wizard:
   ```python
   unraid(action="health", subaction="setup")
   ```

3. The wizard prompts for:
   - **API URL**: Your Unraid GraphQL endpoint (e.g. `https://10-1-0-2.xxx.myunraid.net:31337`)
   - **API Key**: Found in Unraid > Settings > Management Access > API Keys

4. Credentials are written to `~/.unraid-mcp/.env` with mode 600.

5. Verify the connection:
   ```python
   unraid(action="health", subaction="test_connection")
   ```

## Option 2: Manual .env setup

1. Clone the repository:
   ```bash
   git clone https://github.com/jmagar/unraid-mcp.git
   cd unraid-mcp
   ```

2. Create the credentials directory and file:
   ```bash
   mkdir -p ~/.unraid-mcp
   cp .env.example ~/.unraid-mcp/.env
   chmod 700 ~/.unraid-mcp
   chmod 600 ~/.unraid-mcp/.env
   ```

3. Edit `~/.unraid-mcp/.env` with your credentials:
   ```bash
   UNRAID_API_URL=https://your-unraid-server
   UNRAID_API_KEY=your_api_key
   ```

4. Install dependencies and start:
   ```bash
   uv sync
   uv run unraid-mcp-server
   ```

## Option 3: Docker deployment

1. Clone and configure:
   ```bash
   git clone https://github.com/jmagar/unraid-mcp.git
   cd unraid-mcp
   ```

2. Set up credentials (the Docker container reads from `~/.claude-homelab/.env` via env_file):
   ```bash
   # Ensure your credentials are in ~/.claude-homelab/.env
   # or modify docker-compose.yaml to point to ~/.unraid-mcp/.env
   ```

3. Start the container:
   ```bash
   docker compose up -d
   ```

4. Verify:
   ```bash
   curl http://localhost:6970/health
   ```

## Option 4: PyPI install

```bash
uvx unraid-mcp
# or
pip install unraid-mcp
unraid-mcp-server
```

## Post-setup verification

After any installation method, verify the setup:

```python
# Test connection
unraid(action="health", subaction="test_connection")

# Run full health check
unraid(action="health", subaction="check")

# Get system overview
unraid(action="system", subaction="overview")
```

## Troubleshooting

**"Credentials not configured"**
- Run `unraid(action="health", subaction="setup")` to configure interactively
- Or create `~/.unraid-mcp/.env` manually from `.env.example`

**"Connection refused"**
- Verify `UNRAID_API_URL` is correct and accessible from the server host
- Check if Unraid's API is enabled in Settings > Management Access

**"SSL verification failed"**
- For self-signed certificates, set `UNRAID_VERIFY_SSL=false` in `.env`
- Only use this in trusted networks

**"Bearer token required"**
- The server auto-generates a token on first HTTP startup
- Check `~/.unraid-mcp/.env` for the generated `UNRAID_MCP_BEARER_TOKEN`
- Configure your MCP client to send it as `Authorization: Bearer <token>`

See [CONFIG](CONFIG.md) for all environment variables and [mcp/AUTH](mcp/AUTH.md) for authentication details.
