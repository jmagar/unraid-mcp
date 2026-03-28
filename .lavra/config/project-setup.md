---
stack: python
review_agents:
  - kieran-python-reviewer
  - code-simplicity-reviewer
  - security-sentinel
  - performance-oracle
plan_review_agents:
  - kieran-python-reviewer
  - code-simplicity-reviewer
disabled_agents: []
---

<reviewer_context_note>
MCP server for Unraid GraphQL API, built with FastMCP. Single consolidated `unraid` tool with action/subaction routing (~108 subactions across 15 domains). Python 3.12+, uv, ruff, ty (Astral type checker), pytest. Async throughout (httpx, asyncio). No web framework — stdio transport by default, streamable-http in Docker. Tests: unit (mock at tool module level), schema validation, HTTP layer (respx), safety (destructive action guards), integration (WebSocket subscriptions). Destructive actions require confirm=True gating.
</reviewer_context_note>
