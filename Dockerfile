# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.29 /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml .
COPY uv.lock .
COPY README.md .

# Copy the source code
COPY unraid_mcp/ ./unraid_mcp/

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

ENV UNRAID_VERIFY_SSL="true"
ENV UNRAID_MCP_LOG_LEVEL="INFO"

# Run unraid-mcp-server.py when the container launches
CMD ["uv", "run", "unraid-mcp-server"]
