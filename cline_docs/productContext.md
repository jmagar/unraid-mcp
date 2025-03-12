# Product Context: Unraid MCP (Model Context Protocol) Server

## Why This Project Exists
The Unraid MCP server project aims to create a bridge between AI assistants (like Claude) and Unraid servers. By implementing the Model Context Protocol (MCP), this server enables AI systems to directly interact with and query Unraid servers through natural language, providing a read-only interface for monitoring and information retrieval.

## Problems It Solves
1. **AI System Integration Gap**: Currently, AI assistants cannot directly interact with Unraid servers, limiting their usefulness in system administration contexts.
2. **Manual Monitoring Overhead**: Requires users to manually execute commands or navigate the UI for routine Unraid monitoring tasks.
3. **Technical Barrier**: Requires users to know specific commands and Unraid terminology to monitor their systems.
4. **API Complexity**: Abstracts the complex GraphQL API behind a more user-friendly interface.
5. **Schema Validation Issues**: Handles inconsistencies and nullable fields in the Unraid GraphQL schema.
6. **Timeout Management**: Properly manages longer operations like disk queries that may take time to complete.
7. **User Information Access**: Simplifies the process of viewing users on the Unraid server.
8. **API Key Visibility**: Provides a secure way to view API keys for Unraid API access.
9. **Unassigned Devices Monitoring**: Makes it easier to view unassigned devices.
10. **Parity History Analysis**: Provides access to historical parity check data for system health monitoring.

## How It Should Work
1. The MCP server acts as an intermediary between AI assistants and the Unraid GraphQL API.
2. AI assistants make natural language requests to the MCP server.
3. The server translates these requests into appropriate GraphQL queries for the Unraid API.
4. Results are formatted and returned to the AI assistant in a comprehensible format.
5. Users can ask questions in natural language about their Unraid server (system info, Docker containers, VMs, array status, etc.) and get appropriate responses.
6. The server handles error conditions gracefully with appropriate retry mechanisms and user feedback.
7. Comprehensive logging provides visibility into operations for debugging and monitoring purposes.
8. Timeout configurations accommodate varying response times from different Unraid API endpoints.
9. User management tools allow for listing users with appropriate permissions.
10. API key management tools provide secure viewing of API keys with role-based permissions.
11. Unassigned devices tools provide detailed information about devices not assigned to the array.
12. Parity history tools offer insights into historical parity check performance and errors.
13. The server uses stdio transport mode exclusively for direct integration with AI assistants.

## Safety Considerations
1. **Read-Only Design**: The server is designed to be read-only, preventing any modifications to the Unraid system.
2. **Removed Dangerous Tools**: All potentially dangerous tools that could modify the system have been removed, including:
   - System shutdown/reboot tools
   - Array start/stop tools
   - Disk mount/unmount tools
   - User add/delete tools
   - API key creation tools
   - Remote access configuration tools
3. **Data Security**: API keys and user credentials must be handled securely.
4. **Information Exposure**: Even with read-only access, sensitive system information could be exposed.
5. **Transport Security**: Using stdio transport mode ensures direct communication with the AI assistant without exposing network ports.
6. **Configuration Security**: Sensitive configuration like API keys should be stored securely in the environment or configuration files.
7. **Disclaimer Requirement**: A clear "Use at Your Own Risk" disclaimer informs users that even read-only tools can expose sensitive information.
