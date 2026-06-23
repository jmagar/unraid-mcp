# syntax=docker/dockerfile:1
# ── Stage 1: Build ──────────────────────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58 AS builder
# Tag in the ref pins Dependabot to the python3.12-bookworm-slim variant (has a shell
# for `RUN uv sync`). Without the tag, Dependabot tracks :latest — a FROM-scratch,
# binary-only image with no /bin/sh — and the build breaks. Digest pinned for reproducibility.

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
FROM python:3.14-slim-bookworm AS runtime
# Runtime Python must match the builder's Python 3.12 virtualenv layout.

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

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER mcp

# Shell-form CMD: /bin/sh expands ${UNRAID_MCP_PORT:-6970} before python runs.
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:${UNRAID_MCP_PORT:-6970}/health', timeout=5).status==200 else 1)" || exit 1

ENTRYPOINT ["/entrypoint.sh"]
