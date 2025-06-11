# Product Context

## Why this project exists

To package the Python MCP server (`unraid-mcp-server.py`) into a portable, isolated, and reproducible Docker container.

## What problems it solves

- Simplifies deployment of the MCP server across different environments.
- Ensures a consistent runtime environment for the server.
- Facilitates easier management and scaling if needed.

## How it should work

A Docker image should be buildable from the provided `Dockerfile`. Running a container from this image should successfully start the `unraid-mcp-server.py` application, making its services available as configured.
