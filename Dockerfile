# syntax=docker/dockerfile:1
# ── Stage 1: Build ──────────────────────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Install dependencies first (cached layer)
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy source and install project
COPY unraid_mcp/ unraid_mcp/
RUN touch README.md LICENSE
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ── Stage 2: Runtime ────────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm AS runtime

RUN groupadd --gid 1000 mcp && \
    useradd --uid 1000 --gid mcp --create-home mcp

WORKDIR /app

# Copy the virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/unraid_mcp /app/unraid_mcp

# Ensure .venv/bin is on PATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create directories with correct ownership.
# /home/mcp/.unraid-mcp is pre-created so Docker named volume mounts inherit mcp ownership.
RUN mkdir -p /app/logs /app/backups /home/mcp/.unraid-mcp && \
    chown -R mcp:mcp /app/logs /app/backups /home/mcp/.unraid-mcp && \
    chmod 700 /home/mcp/.unraid-mcp

# Default env — overridden by .env / docker-compose
ENV UNRAID_MCP_TRANSPORT=streamable-http \
    UNRAID_MCP_HOST=0.0.0.0 \
    UNRAID_MCP_PORT=6970 \
    UNRAID_MCP_LOG_LEVEL=INFO

EXPOSE 6970

RUN apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER mcp

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD wget --quiet --tries=1 --spider \
        "http://localhost:${UNRAID_MCP_PORT:-6970}/health" || exit 1

ENTRYPOINT ["/entrypoint.sh"]
