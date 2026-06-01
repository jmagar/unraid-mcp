# syntax=docker/dockerfile:1.7

FROM rust:1.90-slim-bookworm AS builder

WORKDIR /app
RUN apt-get update && apt-get install -y pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*

# Cache deps layer — build a stub binary first so dependency compilation
# is cached independently from source changes.
COPY Cargo.toml Cargo.lock ./
# Strip xtask workspace member — not needed in Docker build context
RUN sed -i 's/, \"xtask\"//g; s/\"xtask\", //g; s/\"xtask\"//g' Cargo.toml
RUN --mount=type=cache,id=unraid-cargo-registry,target=/usr/local/cargo/registry,sharing=locked \
    --mount=type=cache,id=unraid-cargo-git,target=/usr/local/cargo/git,sharing=locked \
    --mount=type=cache,id=unraid-cargo-target,target=/app/target,sharing=locked \
    mkdir src && echo "fn main() {}" > src/main.rs && cargo build --release --locked -p unraid-mcp && rm -rf src

# Build real binary
COPY src/ src/
RUN --mount=type=cache,id=unraid-cargo-registry,target=/usr/local/cargo/registry,sharing=locked \
    --mount=type=cache,id=unraid-cargo-git,target=/usr/local/cargo/git,sharing=locked \
    --mount=type=cache,id=unraid-cargo-target,target=/app/target,sharing=locked \
    touch src/main.rs && cargo build --release --locked -p unraid-mcp && cp target/release/runraid /usr/local/bin/runraid

# Runtime image — minimal Debian with TLS certs and curl for healthcheck
FROM debian:bookworm-slim
RUN apt-get update && \
    apt-get install -y ca-certificates curl gosu && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/bin/runraid /usr/local/bin/runraid
COPY entrypoint.sh /entrypoint.sh

RUN groupadd --gid 1000 unraid && \
    useradd --uid 1000 --gid unraid --no-create-home --shell /sbin/nologin unraid && \
    mkdir -p /data && chown unraid:unraid /data && \
    chmod +x /entrypoint.sh

ENV RUST_LOG=info

VOLUME ["/data"]

EXPOSE 40010/tcp

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -sf http://localhost:40010/health || exit 1

LABEL io.modelcontextprotocol.server.name="tv.tootie/unraid-mcp"

# entrypoint validates env, sets up /data, then drops to 1000:1000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["serve", "mcp"]
