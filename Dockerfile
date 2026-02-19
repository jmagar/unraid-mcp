# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Create non-root user with home directory and give ownership of /app
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --create-home --shell /bin/false appuser && \
    chown appuser:appuser /app

# Copy dependency files (owned by appuser via --chown)
COPY --chown=appuser:appuser pyproject.toml .
COPY --chown=appuser:appuser uv.lock .
COPY --chown=appuser:appuser README.md .
COPY --chown=appuser:appuser LICENSE .

# Copy the source code
COPY --chown=appuser:appuser unraid_mcp/ ./unraid_mcp/

# Switch to non-root user before installing dependencies
USER appuser

# Install dependencies and the package
RUN uv sync --frozen

# Make port UNRAID_MCP_PORT available to the world outside this container
# Defaulting to 6970, but can be overridden by environment variable
EXPOSE 6970

# Define environment variables (defaults, can be overridden at runtime)
ENV UNRAID_MCP_PORT=6970
ENV UNRAID_MCP_HOST="0.0.0.0"
ENV UNRAID_MCP_TRANSPORT="streamable-http"
ENV UNRAID_API_URL=""
ENV UNRAID_API_KEY=""
ENV UNRAID_VERIFY_SSL="true"
ENV UNRAID_MCP_LOG_LEVEL="INFO"

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:6970/mcp')"]

# Run unraid-mcp-server when the container launches
CMD ["uv", "run", "unraid-mcp-server"]
