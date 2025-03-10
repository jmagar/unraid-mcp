# Product Context: Unraid MCP (Model Context Protocol) Server

## Why This Project Exists
The Unraid MCP server project aims to create a bridge between AI assistants (like Claude) and Unraid servers. By implementing the Model Context Protocol (MCP), this server enables AI systems to directly interact with, query, and manage Unraid servers through natural language.

## Problems It Solves
1. **AI System Integration Gap**: Currently, AI assistants cannot directly interact with Unraid servers, limiting their usefulness in system administration contexts.
2. **Manual Administration Overhead**: Requires users to manually execute commands or navigate the UI for routine Unraid management tasks.
3. **Technical Barrier**: Requires users to know specific commands and Unraid terminology to manage their systems.

## How It Should Work
1. The MCP server acts as an intermediary between AI assistants and the Unraid GraphQL API.
2. AI assistants make natural language requests to the MCP server.
3. The server translates these requests into appropriate GraphQL queries/mutations for the Unraid API.
4. Results are formatted and returned to the AI assistant in a comprehensible format.
5. Users can ask questions or issue commands in natural language about their Unraid server (system info, Docker containers, VMs, array status, etc.) and get appropriate responses or actions. 