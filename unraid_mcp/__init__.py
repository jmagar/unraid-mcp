"""Unraid MCP Server Package.

A modular MCP (Model Context Protocol) server that provides tools to interact
with an Unraid server's GraphQL API.
"""

from importlib.metadata import PackageNotFoundError, version


try:
    __version__ = version("unraid-mcp")
except PackageNotFoundError:
    __version__ = "0.0.0"
