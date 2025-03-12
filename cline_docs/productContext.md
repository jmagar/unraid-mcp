# Product Context: Unraid MCP (Model Context Protocol) Server

## Why This Project Exists
The Unraid MCP server project aims to create a bridge between AI assistants (like Claude) and Unraid servers. By implementing the Model Context Protocol (MCP), this server enables AI systems to directly interact with, query, and manage Unraid servers through natural language.

## Problems It Solves
1. **AI System Integration Gap**: Currently, AI assistants cannot directly interact with Unraid servers, limiting their usefulness in system administration contexts.
2. **Manual Administration Overhead**: Requires users to manually execute commands or navigate the UI for routine Unraid management tasks.
3. **Technical Barrier**: Requires users to know specific commands and Unraid terminology to manage their systems.
4. **API Complexity**: Abstracts the complex GraphQL API behind a more user-friendly interface.
5. **Schema Validation Issues**: Handles inconsistencies and nullable fields in the Unraid GraphQL schema.
6. **Timeout Management**: Properly manages longer operations like disk queries that may take time to complete.
7. **User Management Complexity**: Simplifies the process of managing users on the Unraid server.
8. **API Key Security**: Provides a secure way to manage API keys for Unraid API access.
9. **Remote Access Configuration**: Simplifies the setup and management of remote access to the Unraid server.
10. **Unassigned Devices Management**: Makes it easier to view and manage unassigned devices.
11. **Parity History Analysis**: Provides access to historical parity check data for system health monitoring.

## How It Should Work
1. The MCP server acts as an intermediary between AI assistants and the Unraid GraphQL API.
2. AI assistants make natural language requests to the MCP server.
3. The server translates these requests into appropriate GraphQL queries/mutations for the Unraid API.
4. Results are formatted and returned to the AI assistant in a comprehensible format.
5. Users can ask questions or issue commands in natural language about their Unraid server (system info, Docker containers, VMs, array status, etc.) and get appropriate responses or actions.
6. The server handles error conditions gracefully with appropriate retry mechanisms and user feedback.
7. Comprehensive logging provides visibility into operations for debugging and monitoring purposes.
8. Timeout configurations accommodate varying response times from different Unraid API endpoints.
9. User management tools allow for listing, adding, and deleting users with appropriate permissions.
10. API key management tools provide secure creation and listing of API keys with role-based permissions.
11. Remote access configuration tools simplify the setup and management of remote access to the Unraid server.
12. Unassigned devices tools provide detailed information about devices not assigned to the array.
13. Parity history tools offer insights into historical parity check performance and errors.
14. The server uses stdio transport mode exclusively for direct integration with AI assistants.

## Safety Considerations
1. **System Modification Risk**: The server provides tools that can modify the Unraid system, including user management and remote access configuration.
2. **Data Security**: API keys and user credentials must be handled securely.
3. **AI Assistant Limitations**: AI assistants may not always understand the full implications of system changes they suggest.
4. **User Verification**: Users should review and approve all system-modifying actions suggested by AI assistants.
5. **Backup Importance**: Regular backups are essential when using tools that can modify system configuration.
6. **Disclaimer Requirement**: A clear "Use at Your Own Risk" disclaimer is necessary to inform users of potential risks.
7. **Transport Security**: Using stdio transport mode ensures direct communication with the AI assistant without exposing network ports.
8. **Configuration Security**: Sensitive configuration like API keys should be stored securely in the environment or configuration files.
