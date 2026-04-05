# Component Inventory -- unraid-mcp

Complete listing of all plugin components.

## MCP tools

| Tool | Type | Module | Description |
| --- | --- | --- | --- |
| `unraid` | Primary | `tools/unraid.py` | Unified action router: 15 domains, 107 subactions |
| `unraid_help` | Helper | `tools/unraid.py` | Returns markdown reference for all actions |
| `diagnose_subscriptions` | Diagnostic | `subscriptions/diagnostics.py` | Inspect subscription states, errors, WebSocket URLs |
| `test_subscription_query` | Diagnostic | `subscriptions/diagnostics.py` | Test a GraphQL subscription query (allowlisted fields) |

## MCP resources

| URI | Source | Description |
| --- | --- | --- |
| `unraid://logs/stream` | `logFileSubscription` | Real-time log stream data |
| `unraid://live/cpu` | `cpu` subscription | Live CPU utilization |
| `unraid://live/memory` | `memory` subscription | Live memory usage |
| `unraid://live/cpu_telemetry` | `cpu_telemetry` subscription | CPU power and temperature |
| `unraid://live/array_state` | `array_state` subscription | Array state changes |
| `unraid://live/parity_progress` | `parity_progress` subscription | Parity check progress |
| `unraid://live/ups_status` | `ups_status` subscription | UPS battery and power |
| `unraid://live/notifications_overview` | `notifications_overview` subscription | Notification counts |
| `unraid://live/owner` | `owner` subscription | Server owner info |
| `unraid://live/server_status` | `server_status` subscription | Server status and connectivity |

## Action domains

| Domain | Subaction count | Module | Destructive? |
| --- | --- | --- | --- |
| `system` | 18 | `tools/_system.py` | No |
| `health` | 4 | `tools/unraid.py` | No |
| `array` | 13 | `tools/_array.py` | Yes (3) |
| `disk` | 6 | `tools/_disk.py` | Yes (1) |
| `docker` | 7 | `tools/_docker.py` | No |
| `vm` | 9 | `tools/_vm.py` | Yes (2) |
| `notification` | 12 | `tools/_notification.py` | Yes (2) |
| `key` | 7 | `tools/_key.py` | Yes (1) |
| `plugin` | 3 | `tools/_plugin.py` | Yes (1) |
| `rclone` | 4 | `tools/_rclone.py` | Yes (1) |
| `setting` | 2 | `tools/_setting.py` | Yes (1) |
| `customization` | 5 | `tools/_customization.py` | No |
| `oidc` | 5 | `tools/_oidc.py` | No |
| `user` | 1 | `tools/_user.py` | No |
| `live` | 11 | `tools/_live.py` | No |

## Middleware chain

| Layer | Class | Purpose |
| --- | --- | --- |
| 1 (outermost) | `LoggingMiddleware` | Logs every tools/call and resources/read with duration |
| 2 | `ErrorHandlingMiddleware` | Converts unhandled exceptions to MCP errors |
| 3 | `SlidingWindowRateLimitingMiddleware` | 540 req/min sliding window |
| 4 (innermost) | `ResponseLimitingMiddleware` | Truncates responses > 512 KB |

## ASGI middleware

| Layer | Class | Purpose |
| --- | --- | --- |
| 1 (outermost) | `HealthMiddleware` | `GET /health` returns 200 without auth |
| 2 | `WellKnownMiddleware` | RFC 9728 OAuth protected resource metadata |
| 3 (innermost) | `BearerAuthMiddleware` | RFC 6750 bearer token validation |

## Plugin manifests

| File | Client | Transport |
| --- | --- | --- |
| `.claude-plugin/plugin.json` | Claude Code | stdio (via `uv run`) |
| `.codex-plugin/plugin.json` | Codex CLI | stdio (via `.mcp.json`) |
| `gemini-extension.json` | Gemini CLI | stdio (via `uv run`) |
| `server.json` | MCP Registry (tv.tootie/unraid-mcp) | stdio (PyPI package) |

## Skills

| Path | Name | Description |
| --- | --- | --- |
| `skills/unraid/SKILL.md` | unraid | Client-facing skill with all domains, subactions, and workflows |

## Hooks

| Hook | Trigger | Script |
| --- | --- | --- |
| Fix env permissions | PostToolUse (Write/Edit/Bash) | `hooks/scripts/fix-env-perms.sh` |
| Ensure ignore files | PostToolUse (Write/Edit/Bash) | `hooks/scripts/ensure-ignore-files.sh` |

## Scripts

| Script | Purpose |
| --- | --- |
| `bin/check-docker-security.sh` | Dockerfile security audit |
| `bin/check-no-baked-env.sh` | Verify no env vars baked into images |
| `bin/check-outdated-deps.sh` | Dependency freshness check |
| `bin/ensure-ignore-files.sh` | Gitignore/dockerignore alignment |
| `bin/generate_unraid_api_reference.py` | Generate canonical API docs and schema change report from GraphQL introspection |
| `bin/validate-marketplace.sh` | Marketplace JSON validation |

## CI/CD workflows

| Workflow | Trigger | Jobs |
| --- | --- | --- |
| `ci.yml` | Push/PR to main | lint, typecheck, test, version-sync, mcp-integration, audit, docker-security |
| `docker-publish.yml` | Push to main/tags | Build multi-arch Docker image, push to ghcr.io, Trivy scan |
| `publish-pypi.yml` | Tag `v*.*.*` | Build, PyPI publish, GitHub release, MCP registry publish |

## Test suites

| Directory | Focus | Count |
| --- | --- | --- |
| `tests/` (root) | Unit tests per domain | 28 test files |
| `tests/safety/` | Destructive action guards | guard verification |
| `tests/schema/` | GraphQL query validation | 119 tests |
| `tests/http_layer/` | httpx request/response | HTTP client tests |
| `tests/integration/` | WebSocket subscription lifecycle | slow, live tests |
| `tests/contract/` | Response shape contracts | shape validation |
| `tests/property/` | Input validation (Hypothesis) | property-based |
