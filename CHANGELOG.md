# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-05-13

### Added

- Initial release of unraid-mcp
- 24 read-only MCP actions via the Unraid GraphQL API
- RMCP Streamable HTTP transport on port 6970
- stdio MCP transport (`unraid mcp`)
- CLI with human-readable and `--json` output for all 24 actions
- Static bearer token auth and OAuth (Google) auth via lab-auth
- `LoopbackDev` auth bypass when bound to 127.x or `UNRAID_MCP_DISABLE_HTTP_AUTH=true`
- `unraid://schema/mcp-tool` MCP resource exposing the tool JSON Schema
- `server_summary` MCP prompt
- Integration tests: auth modes, CLI help, OAuth flow, RMCP compat, stdio transport
