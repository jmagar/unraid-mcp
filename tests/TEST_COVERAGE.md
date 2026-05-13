# TEST_COVERAGE.md — `tests/test_live.sh`

## 1. Overview

`tests/test_live.sh` is the canonical integration test suite for the **syslog-mcp** MCP server. It exercises the server end-to-end over HTTP using real JSON-RPC requests, not unit stubs or mocks.

**Service under test:** syslog-mcp — a read-only MCP server that exposes syslog data from a SQLite backing store via the Model Context Protocol (MCP) over HTTP.

**MCP server exercised:** The HTTP transport endpoint at `POST /mcp`, plus the unauthenticated health check at `GET /health`. All MCP calls use JSON-RPC 2.0.

**What it does NOT test:**
- Syslog ingestion (UDP/TCP listeners)
- Write operations of any kind (there are none in the tool surface, but the principle applies)
- Stdio transport (see section 9)
- Long-running streaming / SSE events beyond accept header negotiation

---

## 2. How to Run

### Prerequisites

| Tool    | Required for         |
|---------|---------------------|
| `curl`  | All modes            |
| `jq`    | All modes            |
| `docker`| `docker` / `all` mode only |

The script checks all prerequisites before running and exits with code `2` if any are missing.

### Modes

#### `docker` / `all` (default)

Builds the Docker image from the project root, starts a container with a tmpfs-backed SQLite store, runs all four test phases, then tears down the container.

```bash
# Minimal — no auth
bash tests/test_live.sh

# With bearer token
SYSLOG_MCP_TOKEN=ci-integration-token bash tests/test_live.sh

# Explicit mode
bash tests/test_live.sh --mode docker

# Alias (identical to docker)
bash tests/test_live.sh --mode all
```

Required env vars: none (token is optional).
Optional env vars:
- `SYSLOG_MCP_TOKEN` — bearer token; if set, auth tests execute and the token is passed to the container.
- `PORT` — overrides the default port `3100` used as fallback when port mapping detection fails.

#### `http`

Tests against a server that is already running. Does not build or manage Docker.

```bash
# Local server on default port
bash tests/test_live.sh --mode http

# Remote server
bash tests/test_live.sh --mode http --url http://192.168.1.10:3100

# Remote server with auth
bash tests/test_live.sh --mode http --url http://192.168.1.10:3100 \
  --token my-secret-token
```

Required env vars: none.
`--url` defaults to `http://localhost:${PORT}` (where `PORT` defaults to `3100`).

#### `stdio` (not implemented)

The script has no `stdio` mode. See section 9 for the reasoning.

### Additional Flags

| Flag        | Effect |
|-------------|--------|
| `--verbose` | Prints raw JSON responses for every tool call to stdout |
| `--help`    | Prints the usage block from the script header and exits `0` |

### Exit Codes

| Code | Meaning |
|------|---------|
| `0`  | All tests passed (SKIPs are not failures) |
| `1`  | One or more tests failed |
| `2`  | Prerequisite missing, Docker build/start failed, or unknown mode |

---

## 3. Test Phases

The script always runs exactly four phases in this order:

```
Phase 1 — Health
Phase 2 — Auth
Phase 3 — Protocol
Phase 4 — Tool calls
```

All four phases run regardless of earlier phase outcomes. A failure in Phase 1 does not abort Phase 2–4.

---

## 4. Every Test — Detailed Assertions

### Phase 1 — Health (`phase_health`)

**Purpose:** Verify the `/health` HTTP endpoint is reachable and reports the server as healthy. This is the baseline liveness check.

**HTTP request:**
```
GET <BASE_URL>/health
Headers: Accept: application/json, text/event-stream
Timeout: 10 seconds
```

| Test label | jq expression | Expected value | PASS condition | FAIL condition |
|---|---|---|---|---|
| `GET /health returns 200` | n/a — uses curl exit code | n/a | curl exits 0 and response is non-empty | curl fails or returns empty body |
| `GET /health — status is ok` | `.status` | `"ok"` | `.status` equals the string `"ok"` | `.status` is missing, null, or any other string |

**Note:** If curl itself fails (non-2xx HTTP or network error), the first test records a FAIL and the function returns early without running the second assertion.

---

### Phase 2 — Auth (`phase_auth`)

**Purpose:** Verify that when a bearer token is configured, the `/mcp` endpoint enforces authentication — rejecting requests with no token and requests with an incorrect token, both with HTTP 401.

**Conditional execution:** Both auth tests are **SKIPPED** (not failed) when `SYSLOG_MCP_TOKEN` is not set. The skip reason is `"SYSLOG_MCP_TOKEN not set — auth assumed disabled"`. This reflects that the server supports running in no-auth mode.

#### Test: `auth: unauthenticated /mcp returns 401`

**HTTP request (no auth header):**

```text
POST <BASE_URL>/mcp
Content-Type: application/json
Accept: application/json, text/event-stream
Body: {"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
Timeout: 10 seconds
```

| Outcome | Condition |
|---------|-----------|
| PASS | HTTP status code is exactly `401` |
| FAIL | HTTP status code is anything other than `401` (actual code is reported) |

#### Test: `auth: bad token returns 401`

**HTTP request (wrong token):**

```text
POST <BASE_URL>/mcp
Authorization: Bearer intentionally-wrong-token-for-testing
Content-Type: application/json
Accept: application/json, text/event-stream
Body: {"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
Timeout: 10 seconds
```

| Outcome | Condition |
|---------|-----------|
| PASS | HTTP status code is exactly `401` |
| FAIL | HTTP status code is anything other than `401` (actual code is reported) |

**Note:** The literal string `intentionally-wrong-token-for-testing` is the hardcoded wrong token. The test does NOT verify that a valid token returns 200 — that is implicitly proved by the subsequent phases succeeding when `AUTH_ARGS` contains the correct token.

---

### Phase 3 — Protocol (`phase_protocol`)

**Purpose:** Verify that the MCP protocol handshake works — `initialize` returns valid server metadata and `tools/list` returns the single `syslog` tool.

#### 3a. `initialize`

**JSON-RPC request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-03-26",
    "capabilities": {},
    "clientInfo": {"name": "test_live.sh", "version": "1.0.0"}
  }
}
```

| Test label | jq expression | PASS condition |
|---|---|---|
| `initialize — protocolVersion present` | `.result.protocolVersion` | Field is non-null, non-empty, non-false |
| `initialize — serverInfo.name present` | `.result.serverInfo.name` | Field is non-null, non-empty, non-false |
| `initialize — capabilities.tools present` | `.result.capabilities.tools` | Field is non-null, non-empty, non-false |

All three use the no-expected-value form of `assert_jq` — they check presence and non-nullness only, not specific values.

#### 3b. `tools/list`

**JSON-RPC request:**
```json
{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
```

| Test label | Check | PASS condition |
|---|---|---|
| `tools/list — returns N tools (expected 1)` | `.result.tools \| length` | Count is `1` |

Then the public tool name is checked:

| Test label | jq expression | Expected value |
|---|---|---|
| `tools/list — tool 'syslog' present` | `.result.tools[] \| select(.name == "syslog") \| .name` | `"syslog"` |

A tool is considered present only if its `.name` field exactly matches the expected string.

---

### Phase 4 — Tool Calls (`phase_tools`)

**Transport mechanics:** Every tool call uses `call_tool`, which:
1. Builds a JSON-RPC `tools/call` request body using `jq -nc`.
2. POSTs to `<BASE_URL>/mcp` with a monotonically incrementing `id`.
3. Extracts `.result.content[0].text` from the raw JSON-RPC response.
4. Parses that text value as JSON (the inner payload), and returns it.

All subsequent assertions operate on this inner JSON payload, not the raw JSON-RPC envelope.

---

#### Tool: `syslog help`

**Arguments:** `{"action":"status"}`. The action has no additional
action-specific parameters.

**Purpose:** Confirm the help tool returns a non-empty help string containing the word "syslog".

| Test label | jq expression | PASS condition |
|---|---|---|
| `syslog help — help field present` | `.help` | Non-null, non-empty, non-false |
| `syslog help — help text is non-empty` | `.help \| length > 0` | Evaluates to `true` |
| `syslog help — help text contains 'syslog'` | `.help \| ascii_downcase \| contains("syslog")` | Evaluates to `true` |

The third assertion is case-insensitive via `ascii_downcase` — the word "syslog" or "Syslog" or "SYSLOG" all pass.

---

#### Tool: `syslog status`

**Arguments:** `{}` (no arguments)

**Purpose:** Confirm the lightweight status action returns DB health and runtime observability without running the heavier stats query.

| Test label | jq expression | PASS condition |
|---|---|---|
| `syslog status — status is ok` | `.status` | Equals `"ok"` |
| `syslog status — db_ok field present` | `.db_ok != null` | Evaluates to `true` |
| `syslog status — runtime_observability present` | `.runtime_observability` | Non-null object |
| `syslog status — otlp counters present` | `.otlp` | Non-null object |

---

#### Tool: `syslog stats`

**Arguments:** `{}` (no arguments)

**Purpose:** Confirm the stats tool returns a valid statistics object with all expected numeric fields.

| Test label | jq expression | PASS condition |
|---|---|---|
| `syslog stats — total_logs field present` | `.total_logs != null` | Evaluates to `true` |
| `syslog stats — total_hosts field present` | `.total_hosts != null` | Evaluates to `true` |
| `syslog stats — logical_db_size_mb present` | `.logical_db_size_mb` | Non-null, non-empty |
| `syslog stats — physical_db_size_mb present` | `.physical_db_size_mb` | Non-null, non-empty |
| `syslog stats — write_blocked field present` | `.write_blocked != null` | Evaluates to `true` |
| `syslog stats — total_logs is a number >= 0` | `.total_logs >= 0` | Evaluates to `true` |
| `syslog stats — total_hosts is a number >= 0` | `.total_hosts >= 0` | Evaluates to `true` |

The `!= null` form is used for `total_logs`, `total_hosts`, and `write_blocked` so that a value of `0` or `false` still passes — these are valid production values. The `>= 0` checks additionally assert numeric type.

---

#### Tool: `syslog hosts`

**Arguments:** `{}` (no arguments)

**Purpose:** Confirm the tool returns a hosts array. If hosts exist, validate each entry's structure.

**Unconditional tests:**

| Test label | jq expression | Expected value |
|---|---|---|
| `syslog hosts — hosts field is an array` | `.hosts \| type` | `"array"` |

**Conditional tests (only run when `.hosts \| length > 0`):**

| Test label | jq expression | PASS condition |
|---|---|---|
| `syslog hosts — entry has hostname field` | `.hosts[0].hostname` | Non-null, non-empty |
| `syslog hosts — entry has log_count field` | `.hosts[0].log_count != null` | Evaluates to `true` |
| `syslog hosts — entry has first_seen field` | `.hosts[0].first_seen` | Non-null, non-empty |
| `syslog hosts — entry has last_seen field` | `.hosts[0].last_seen` | Non-null, non-empty |

**Skipped when:** `hosts` array is empty. Skip reason: `"no hosts in DB (no syslog data ingested)"`. This is expected in a fresh CI container with no ingested syslog traffic.

---

#### Tool: `syslog search` (with query)

**Arguments:** `{"query": "error", "limit": 10}`

**Purpose:** Confirm a keyword search returns a properly structured result.

**Unconditional tests:**

| Test label | jq expression | PASS condition |
|---|---|---|
| `syslog search — count field present` | `.count != null` | Evaluates to `true` |
| `syslog search — logs field is array` | `.logs \| type` | `"array"` |
| `syslog search — count is number >= 0` | `.count >= 0` | Evaluates to `true` |

**Conditional tests (only run when `.logs \| length > 0`):**

| Test label | jq expression | PASS condition |
|---|---|---|
| `syslog search — log entry has message field` | `.logs[0].message` | Non-null, non-empty |
| `syslog search — log entry has hostname field` | `.logs[0].hostname` | Non-null, non-empty |
| `syslog search — log entry has severity field` | `.logs[0].severity` | Non-null, non-empty |
| `syslog search — log entry has timestamp field` | `.logs[0].timestamp` | Non-null, non-empty |

**Skipped when:** No logs match the query `"error"`. Skip reason: `"no matching logs (empty DB)"`.

#### Tool: `syslog search` (no query — list recent)

A second invocation with different arguments, run immediately after the first:

**Arguments:** `{"limit": 5}`

**Purpose:** Confirm the tool works without a query (browsing mode — returns most recent logs).

| Test label | jq expression | PASS condition |
|---|---|---|
| `syslog search (no query) — count field present` | `.count != null` | Evaluates to `true` |
| `syslog search (no query) — logs field is array` | `.logs \| type` | `"array"` |

No per-entry field validation on this second call — it only checks the envelope shape.

---

#### Tool: `syslog errors`

**Arguments:** `{"limit": 10}`

**Purpose:** Confirm the error-summary tool returns a valid summary array for error-level logs.

**Unconditional tests:**

| Test label | jq expression | Expected value |
|---|---|---|
| `syslog errors — summary field is array` | `.summary \| type` | `"array"` |

**Conditional tests (only run when `.summary \| length > 0`):**

| Test label | jq expression | PASS condition |
|---|---|---|
| `syslog errors — entry has hostname field` | `.summary[0].hostname` | Non-null, non-empty |
| `syslog errors — entry has severity field` | `.summary[0].severity` | Non-null, non-empty |
| `syslog errors — entry has count field` | `.summary[0].count != null` | Evaluates to `true` |

**Skipped when:** No error-level logs in the database. Skip reason: `"no error-level logs in DB"`.

---

#### Tool: `syslog tail`

**Arguments:** `{"n": 10}`

**Purpose:** Confirm the tail tool returns the N most recent log entries with the correct structure.

**Unconditional tests:**

| Test label | jq expression | PASS condition |
|---|---|---|
| `syslog tail — count field present` | `.count != null` | Evaluates to `true` |
| `syslog tail — logs field is array` | `.logs \| type` | `"array"` |
| `syslog tail — count is number >= 0` | `.count >= 0` | Evaluates to `true` |

**Conditional tests (only run when `.logs \| length > 0`):**

| Test label | jq expression | PASS condition |
|---|---|---|
| `syslog tail — entry has message field` | `.logs[0].message` | Non-null, non-empty |
| `syslog tail — entry has hostname field` | `.logs[0].hostname` | Non-null, non-empty |
| `syslog tail — entry has severity field` | `.logs[0].severity` | Non-null, non-empty |
| `syslog tail — entry has timestamp field` | `.logs[0].timestamp` | Non-null, non-empty |

**Skipped when:** No logs in database. Skip reason: `"no logs in DB"`.

---

#### Tool: `syslog correlate`

**Arguments (dynamically built):**
```json
{
  "reference_time": "<current UTC time in ISO 8601>",
  "window_minutes": 5,
  "severity_min": "debug",
  "limit": 50
}
```

The `reference_time` is generated at test runtime via `date -u +%Y-%m-%dT%H:%M:%SZ`. The `jq -nc` call with `--arg t` injects it safely.

**Purpose:** Confirm the correlation tool returns a complete temporal window object. This is the most structurally rich response — it validates both metadata fields and the envelope of correlated data.

| Test label | jq expression | PASS condition |
|---|---|---|
| `syslog correlate — reference_time present` | `.reference_time` | Non-null, non-empty |
| `syslog correlate — window_minutes present` | `.window_minutes != null` | Evaluates to `true` |
| `syslog correlate — window_from present` | `.window_from` | Non-null, non-empty |
| `syslog correlate — window_to present` | `.window_to` | Non-null, non-empty |
| `syslog correlate — hosts field is array` | `.hosts \| type` | `"array"` |
| `syslog correlate — total_events >= 0` | `.total_events >= 0` | Evaluates to `true` |
| `syslog correlate — truncated field present` | `.truncated != null` | Evaluates to `true` |

All seven assertions are unconditional — `syslog correlate` is expected to always return all metadata fields even when the time window contains zero events. The `window_from` and `window_to` fields prove the server computed temporal bounds correctly. The `truncated` field (boolean) proves the pagination logic field is always present regardless of data volume.

---

## 5. Skipped Operations and Why

### Tests that are conditionally skipped

| Skip label | Condition | Reason |
|---|---|---|
| `auth: unauthenticated /mcp returns 401` | `SYSLOG_MCP_TOKEN` not set | Auth assumed disabled; enforcing 401 without a configured token is not the server's job |
| `auth: bad token returns 401` | `SYSLOG_MCP_TOKEN` not set | Same as above |
| `syslog hosts — entry field validation` | `hosts` array is empty | No syslog data has been ingested; empty array is valid |
| `syslog search — log entry field validation` | No logs matching `"error"` | Empty DB is valid; field shape only verified when data exists |
| `syslog errors — entry field validation` | `summary` array is empty | No error-level logs; empty is valid |
| `syslog tail — entry field validation` | No logs in DB | Empty DB; field shape only verified when data exists |

### Operations that are entirely absent from the script

No write operations exist in the syslog-mcp tool surface (it is a read-only server), so there is nothing to exclude on data-safety grounds. The script tests every action on the `syslog` tool:

| Action | Tested? |
|---|---|
| `syslog search` | Yes — two invocations |
| `syslog tail` | Yes |
| `syslog errors` | Yes |
| `syslog hosts` | Yes |
| `syslog correlate` | Yes |
| `syslog stats` | Yes |
| `syslog status` | Yes |
| `syslog help` | Yes |

---

## 6. What "Proving Correct Operation" Means Per Tool

| Action | What correctness means beyond "responded" |
|---|---|
| `syslog help` | `.help` is a non-empty string that mentions "syslog" — proves the help content is not empty or boilerplate |
| `syslog status` | `.status`, `.db_ok`, `.runtime_observability`, and `.otlp` are present — proves the lightweight runtime health path works through MCP |
| `syslog stats` | All numeric fields are present AND `>= 0` — proves the DB query ran and returned sensible (not negative) values; `write_blocked` is proven non-null (may be `false`) |
| `syslog hosts` | `.hosts` is a JSON array (not an object or string); if populated, each entry has `hostname`, `log_count`, `first_seen`, `last_seen` — proves the host aggregation query produced correctly shaped rows |
| `syslog search` | `.count` is numeric `>= 0` and `.logs` is an array; if populated, entries have all four log fields — proves the full-text search plumbing returns correctly shaped log rows |
| `syslog errors` | `.summary` is an array; if populated, entries have `hostname`, `severity`, and `count` — proves the severity-filtered aggregation returns the correct schema |
| `syslog tail` | `.count >= 0` and `.logs` is an array; if populated, entries have all four log fields — proves the recency ordering query returns correct log rows |
| `syslog correlate` | All seven fields (`reference_time`, `window_minutes`, `window_from`, `window_to`, `hosts`, `total_events`, `truncated`) are present — proves the temporal windowing logic computed bounds and populated all metadata even on an empty window |

---

## 7. Authentication Tests

The auth phase covers exactly two negative scenarios. Positive auth (correct token accepted) is proven implicitly by all Phase 3 and Phase 4 tests passing when `TOKEN` is non-empty.

| Scenario | Method | Token sent | Expected HTTP code |
|---|---|---|---|
| No auth header | POST /mcp | None | 401 |
| Wrong token | POST /mcp | `intentionally-wrong-token-for-testing` (literal) | 401 |
| Correct token | POST /mcp | Value of `TOKEN` | Implicit — Phase 3/4 pass |

The `/health` endpoint is tested without any auth header and is expected to return 200. This verifies that health is publicly accessible regardless of auth configuration.

---

## 8. Docker Mode Specifics

### Image Build

```bash
docker build -t syslog-mcp-test <project_root>
```

The project root is resolved by navigating one directory up from the script's location (`dirname "$BASH_SOURCE[0]"` + `/..`), then canonicalized with `pwd -P`. The image tag is the hardcoded string `syslog-mcp-test`.

On build failure, the script exits with code `2`.

### Container Start

```bash
docker run \
  --name syslog-mcp-test-$$ \
  --detach \
  --rm \
  -p 0:3100 \
  --tmpfs /data:rw,noexec,nosuid,size=64m \
  [-e SYSLOG_MCP_TOKEN=<token>] \
  -e SYSLOG_MCP_MAX_DB_SIZE_MB=0 \
  -e SYSLOG_MCP_RECOVERY_DB_SIZE_MB=0 \
  -e SYSLOG_MCP_MIN_FREE_DISK_MB=0 \
  -e SYSLOG_MCP_RECOVERY_FREE_DISK_MB=0 \
  syslog-mcp-test
```

Key design decisions:

| Decision | Rationale |
|---|---|
| `--name syslog-mcp-test-$$` | Uses the shell PID to avoid container name collisions between parallel test runs |
| `-p 0:3100` | Docker assigns a random host port — avoids conflicts with existing processes on port 3100 |
| `--tmpfs /data:rw,noexec,nosuid,size=64m` | SQLite database lives entirely in memory — no disk I/O, no volume cleanup, always starts clean |
| `SYSLOG_MCP_MAX_DB_SIZE_MB=0` etc. | Zeroes out storage budget limits that would conflict with the tmpfs size cap |
| `SYSLOG_MCP_TOKEN` | Conditionally passed only when `TOKEN` is non-empty |

### Port Discovery

After the container starts, the actual mapped host port is discovered via:
```bash
docker inspect <container> \
  --format '{{(index (index .NetworkSettings.Ports "3100/tcp") 0).HostPort}}'
```

If this fails (empty result), the script falls back to `$PORT` (default `3100`) with a warning. `BASE_URL` is then set to `http://localhost:<mapped_port>`.

### Health Polling

The script polls `GET <BASE_URL>/health` in a loop:
- Maximum 30 attempts, 1 second sleep between each.
- Considers the server healthy when `jq -r '.status'` returns `"ok"`.
- On timeout (30 attempts exhausted), dumps the last 30 lines of `docker logs <container>` to stderr and returns exit code `2`.

### Teardown

A `trap docker_cleanup EXIT INT TERM` is registered immediately before the build step. The cleanup function runs:
```bash
docker rm -f <container_name>
```

The container was started with `--rm`, so Docker also removes it on exit — the explicit `rm -f` is a belt-and-suspenders safeguard.

---

## 9. Stdio Mode

The script has **no stdio mode**. There is no `--mode stdio` option and no stdio-related code paths.

This is appropriate because:
- The syslog-mcp server exposes the MCP HTTP transport, not the stdio transport.
- Stdio transport would require spawning the server binary as a subprocess and piping JSON-RPC messages over stdin/stdout, which is a different integration surface.
- All MCP tools are fully exercised via the HTTP transport in Phase 3 and Phase 4.

If a future stdio transport is added to syslog-mcp, a corresponding mode would need to be added to this script.

---

## 10. Output Format and Interpreting Results

### Per-test output

Each test prints one line:

```
[PASS] <test label>
[FAIL] <test label>
       expected '<value>', got '<value>'
[SKIP] <test label> — <reason>
```

Color coding is applied when stdout is a terminal and `NO_COLOR` is unset:
- `[PASS]` — green
- `[FAIL]` — red
- `[SKIP]` — yellow

### Section headers

Each phase and sub-section is announced with:
```
=== Phase N — <name> ===
```

### Verbose mode

When `--verbose` is passed, every tool call additionally prints:
```
[VERBOSE] <tool_name> response:
<raw JSON-RPC response>
```

This shows the complete JSON-RPC envelope including `.result.content[0].text` before inner JSON parsing.

### Summary block

At the end, a 65-character wide summary is printed:

```
=================================================================
PASS                  42
FAIL                   0
SKIP                   6
TOTAL                 48
=================================================================
```

If any tests failed, a bulleted list of failed test labels follows:
```
Failed tests:
  • <test label>
  • <test label>
```

### Interpreting SKIPs

SKIPs are **not failures**. They indicate the test was logically valid but could not execute due to a missing precondition (typically an empty database). In a CI environment bootstrapped with no syslog traffic, several per-entry field validation tests will SKIP — this is the expected and correct behavior. To exercise those tests, pre-populate the SQLite database with syslog entries before running.

### Interpreting FAILs

A FAIL always includes a reason line. Common patterns:

| Reason pattern | Likely cause |
|---|---|
| `expected 'ok', got ''` | `/health` returned non-JSON or server not started |
| `expression '.field' returned 'null'` | Tool response missing an expected field — schema mismatch |
| `got HTTP 000` | Server unreachable (connection refused) |
| `got HTTP 200` on auth tests | Auth not configured on the server but `TOKEN` is set in the test runner |
| `curl failed for tool <name>` | Network error or server crashed during test |
