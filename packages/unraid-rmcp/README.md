# unraid-rmcp

Node launcher for the `runraid` Rust MCP server and CLI binary.

```bash
npx -y unraid-rmcp --help
```

The package downloads the matching GitHub Release binary during `postinstall`.

## MCP stdio

```json
{
  "mcpServers": {
    "unraid-rmcp": {
      "command": "npx",
      "args": ["-y", "unraid-rmcp"]
    }
  }
}
```

## Environment

- `UNRAID_RMCP_BINARY_VERSION`: release tag/version to download, defaulting to this npm package version.
- `UNRAID_RMCP_VERSION`: alias for `UNRAID_RMCP_BINARY_VERSION`.
- `UNRAID_RMCP_REPO`: GitHub `owner/repo`, defaulting to `jmagar/unraid-rmcp`.
- `UNRAID_RMCP_RELEASE_BASE_URL`: full release download base URL.
- `UNRAID_RMCP_SKIP_DOWNLOAD=1`: skip postinstall download.
