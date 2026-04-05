# Live Smoke Testing (mcporter)

End-to-end verification against a running unraid-mcp server. Complements unit/integration tests in [TESTS.md](TESTS.md).

## Purpose

Mcporter tests verify that the MCP server responds correctly over both HTTP and stdio transports with real GraphQL queries against a live Unraid API.

## Test scripts

### HTTP smoke test (`test-actions.sh`)

Tests all non-destructive actions over HTTP transport:

```bash
./tests/mcporter/test-actions.sh [MCP_URL]
# Default: http://localhost:6970/mcp
```

Sends tool calls for every non-destructive action/subaction combination and validates response format.

### stdio smoke test (`test-tools.sh`)

Tests tool availability without a running HTTP server:

```bash
./tests/mcporter/test-tools.sh [--parallel] [--timeout-ms N] [--verbose]
```

Spawns the server in stdio mode and sends tool list/call requests over stdin/stdout. Good for CI environments where no network is needed.

### Destructive action smoke test (`test-destructive.sh`)

Confirms that destructive action guards block execution without `confirm=True`:

```bash
./tests/mcporter/test-destructive.sh [MCP_URL]
```

Sends destructive subactions without `confirm=True` and verifies the server returns an error (not execution).

### HTTP e2e test (`test-http.sh`)

Full HTTP transport test with automatic bearer token loading:

```bash
# Standard (reads token from ~/.unraid-mcp/.env)
just test-http

# Skip auth (for gateway-protected deployments)
just test-http-no-auth

# Remote URL
just test-http-remote https://unraid.tootie.tv/mcp
```

## Justfile recipes

| Recipe | Description |
|--------|-------------|
| `just test-http` | HTTP e2e test with auto-read token |
| `just test-http-no-auth` | HTTP e2e test without auth |
| `just test-http-remote <url>` | HTTP e2e test against a remote URL |
| `just test-live` | Run pytest integration tests (`-m live`) |

## Transport differences

| Aspect | HTTP (`test-actions.sh`) | stdio (`test-tools.sh`) |
|--------|--------------------------|------------------------|
| Server required | Yes (running on port) | No (spawned inline) |
| Auth | Bearer token | None |
| Network | HTTP to `/mcp` | stdin/stdout pipes |
| CI friendly | Needs Docker or port | Yes (process only) |
| Parallelism | Native (concurrent HTTP) | Optional (`--parallel`) |

## CI integration

The `ci.yml` workflow runs `test_live.sh` in the `mcp-integration` job:
- Only runs on pushes and same-repo PRs (needs secrets)
- Uses `UNRAID_API_URL` and `UNRAID_API_KEY` from GitHub secrets
- Validates real GraphQL connectivity

## See Also

- [TESTS.md](TESTS.md) -- Unit and specialized test suites
- [CICD.md](CICD.md) -- CI workflow configuration
- [../GUARDRAILS.md](../GUARDRAILS.md) -- Destructive action guard details
