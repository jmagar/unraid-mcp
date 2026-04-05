# Technology Stack Documentation -- unraid-mcp

## Files

| File | Description |
|------|-------------|
| [TECH.md](TECH.md) | Technology choices and rationale |
| [ARCH.md](ARCH.md) | Architecture overview and component diagram |
| [PRE-REQS.md](PRE-REQS.md) | Prerequisites and system requirements |

## Stack summary

- **Language**: Python 3.12+
- **MCP framework**: FastMCP 3.0+
- **HTTP client**: httpx (async)
- **WebSocket**: websockets 15.0+
- **Web framework**: FastAPI + Uvicorn (via FastMCP)
- **Validation**: Pydantic (via FastMCP)
- **Package manager**: uv
- **Build system**: Hatchling
- **Linting**: Ruff
- **Type checking**: ty (Astral)
- **Testing**: pytest + pytest-asyncio + respx + hypothesis
- **Container**: Docker (multi-stage, Python 3.12 slim)

## Cross-References

- [mcp/](../mcp/) -- MCP server specifics
- [repo/](../repo/) -- Repository structure
- [upstream/](../upstream/) -- Unraid GraphQL API details
