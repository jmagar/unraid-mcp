# Mock GraphQL server (schema-faithful, offline)

A JS mock GraphQL server that serves the bundled SDL
(`docs/unraid/UNRAID-SCHEMA.graphql`) with
[`@graphql-tools/mock`](https://the-guild.dev/graphql/tools/docs/mocking)
(`addMocksToSchema`) on top of [graphql-yoga](https://the-guild.dev/graphql/yoga-server).

The Python `tests/mock/test_mock_roundtrip.py` tests point the **real** Unraid
client at it, so the actual `httpx → GraphQL` round trip and the middleware stack
run end-to-end **without a live Unraid server**. Because responses are generated
*from the schema*, a field rename in the SDL makes the round-trip fail instead of
silently returning stale data — the exact class of bug that motivated this
(e.g. `isInitialSetup` → `isFreshInstall`).

## One-time setup (then fully offline)

```bash
npm --prefix tests/mock install
```

## Run

```bash
# the mock round-trip tests (auto-skip if node_modules is absent)
uv run pytest tests/mock -m mockserver

# or run the server standalone and point any client at it
MOCK_PORT=9002 npm --prefix tests/mock start
#   → http://127.0.0.1:9002/graphql   (GraphiQL at the same URL in a browser)
```

The pytest fixture (`tests/mock/conftest.py`) boots the server on a free port once
per session and restores `settings.UNRAID_API_URL`/`UNRAID_API_KEY` afterward.

## Mocking layers in this repo

| Layer | Tool | Where |
|-------|------|-------|
| Handler logic / value assertions | `unittest.mock` on `make_graphql_request` | most `tests/*.py` |
| HTTP transport (errors, timeouts, status) | `respx` | `tests/http_layer/` |
| Query/mutation validity vs SDL | `graphql-core` (`validate`) | `tests/schema/` |
| **Schema-faithful HTTP round trip** | **`@graphql-tools/mock` + graphql-yoga (this dir)** | `tests/mock/` |

## Scope / caveats

- **Queries + mutations only.** The `live` domain uses `graphql-transport-ws`
  subscriptions over WebSocket, which this HTTP server does **not** mock.
- **Values are mock/static** (custom scalars in `mock-server.mjs`). Use this to
  prove the plumbing + schema validity, not to assert specific business values —
  keep the dict-mock unit tests for that.
- **Abstract types** (interfaces/unions) need a `__resolveType`; the round-trip
  tests deliberately query concrete fields. Add resolvers in `mock-server.mjs` if
  you extend coverage to abstract selections.
- **CI:** these tests skip unless `node_modules` is present, so they don't run in
  the Python-only CI by default. Add an `npm --prefix tests/mock install` step to
  a workflow if you want them in CI.
