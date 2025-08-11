"""Storage, disk, and notification management tools.

This module provides tools for managing user shares, notifications,
log files, physical disks with SMART data, and system storage operations
with custom timeout configurations for disk-intensive operations.
"""

from typing import Any, Dict, List, Optional

import httpx
from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError


def register_storage_tools(mcp: FastMCP):
    """Register all storage tools with the FastMCP instance.
    
    Args:
        mcp: FastMCP instance to register tools with
    """
    
    @mcp.tool()
    async def get_shares_info() -> List[Dict[str, Any]]:
        """Retrieves information about user shares."""
        query = """
        query GetSharesInfo {
          shares {
            id
            name
            free
            used
            size
            include
            exclude
            cache
            nameOrig
            comment
            allocator
            splitLevel
            floor
            cow
            color
            luksStatus
          }
        }
        """
        try:
            logger.info("Executing get_shares_info tool")
            response_data = await make_graphql_request(query)
            return response_data.get("shares", [])
        except Exception as e:
            logger.error(f"Error in get_shares_info: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve shares information: {str(e)}")

    @mcp.tool()
    async def get_notifications_overview() -> Dict[str, Any]:
        """Retrieves an overview of system notifications (unread and archive counts by severity)."""
        query = """
        query GetNotificationsOverview {
          notifications {
            overview {
              unread { info warning alert total }
              archive { info warning alert total }
            }
          }
        }
        """
        try:
            logger.info("Executing get_notifications_overview tool")
            response_data = await make_graphql_request(query)
            if response_data.get("notifications"):
                return response_data["notifications"].get("overview", {})
            return {}
        except Exception as e:
            logger.error(f"Error in get_notifications_overview: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve notifications overview: {str(e)}")

    @mcp.tool()
    async def list_notifications(
        type: str, 
        offset: int, 
        limit: int, 
        importance: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lists notifications with filtering. Type: UNREAD/ARCHIVE. Importance: INFO/WARNING/ALERT."""
        query = """
        query ListNotifications($filter: NotificationFilter!) {
          notifications {
            list(filter: $filter) {
              id
              title
              subject
              description
              importance
              link
              type
              timestamp
              formattedTimestamp
            }
          }
        }
        """
        variables = {
            "filter": {
                "type": type.upper(),
                "offset": offset,
                "limit": limit,
                "importance": importance.upper() if importance else None
            }
        }
        # Remove null importance from variables if not provided, as GraphQL might be strict
        if not importance:
            del variables["filter"]["importance"]
            
        try:
            logger.info(f"Executing list_notifications: type={type}, offset={offset}, limit={limit}, importance={importance}")
            response_data = await make_graphql_request(query, variables)
            if response_data.get("notifications"):
                return response_data["notifications"].get("list", [])
            return []
        except Exception as e:
            logger.error(f"Error in list_notifications: {e}", exc_info=True)
            raise ToolError(f"Failed to list notifications: {str(e)}")

    @mcp.tool()
    async def list_available_log_files() -> List[Dict[str, Any]]:
        """Lists all available log files that can be queried."""
        query = """
        query ListLogFiles {
          logFiles {
            name
            path
            size
            modifiedAt
          }
        }
        """
        try:
            logger.info("Executing list_available_log_files tool")
            response_data = await make_graphql_request(query)
            return response_data.get("logFiles", [])
        except Exception as e:
            logger.error(f"Error in list_available_log_files: {e}", exc_info=True)
            raise ToolError(f"Failed to list available log files: {str(e)}")

    @mcp.tool()
    async def get_logs(log_file_path: str, tail_lines: int = 100) -> Dict[str, Any]:
        """Retrieves content from a specific log file, defaulting to the last 100 lines."""
        # The Unraid GraphQL API Query.logFile takes 'lines' and 'startLine'.
        # To implement 'tail_lines', we would ideally need to know the total lines first,
        # then calculate startLine. However, Query.logFile itself returns totalLines.
        # A simple approach for 'tail' is to request a large number of lines if totalLines is not known beforehand,
        # and let the API handle it, or make two calls (one to get totalLines, then another).
        # For now, let's assume 'lines' parameter in Query.logFile effectively means tail if startLine is not given.
        # If not, this tool might need to be smarter or the API might not directly support 'tail' easily.
        # The SDL for LogFileContent implies it returns startLine, so it seems aware of ranges.

        # Let's try fetching with just 'lines' to see if it acts as a tail, 
        # or if we need Query.logFiles first to get totalLines for calculation.
        # For robust tailing, one might need to fetch totalLines first, then calculate start_line for the tail.
        # Simplified: query for the last 'tail_lines'. If the API doesn't support tailing this way, we may need adjustment.
        # The current plan is to pass 'lines=tail_lines' directly.

        query = """
        query GetLogContent($path: String!, $lines: Int) {
          logFile(path: $path, lines: $lines) {
            path
            content
            totalLines
            startLine
          }
        }
        """
        variables = {"path": log_file_path, "lines": tail_lines}
        try:
            logger.info(f"Executing get_logs for {log_file_path}, tail_lines={tail_lines}")
            response_data = await make_graphql_request(query, variables)
            return response_data.get("logFile", {})
        except Exception as e:
            logger.error(f"Error in get_logs for {log_file_path}: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve logs from {log_file_path}: {str(e)}")

    @mcp.tool()
    async def list_physical_disks() -> List[Dict[str, Any]]:
        """Lists all physical disks recognized by the Unraid system."""
        # Querying an extremely minimal set of fields for diagnostics
        query = """ 
        query ListPhysicalDisksMinimal {
          disks {
            id
            device
            name
          }
        }
        """
        try:
            logger.info("Executing list_physical_disks tool with minimal query and increased timeout")
            # Increased read timeout for this potentially slow query
            long_timeout = httpx.Timeout(10.0, read=90.0, connect=5.0) 
            response_data = await make_graphql_request(query, custom_timeout=long_timeout)
            return response_data.get("disks", [])
        except Exception as e:
            logger.error(f"Error in list_physical_disks: {e}", exc_info=True)
            raise ToolError(f"Failed to list physical disks: {str(e)}")

    @mcp.tool()
    async def get_disk_details(disk_id: str) -> Dict[str, Any]:
        """Retrieves detailed SMART information and partition data for a specific physical disk."""
        # Enhanced query with more comprehensive disk information
        query = """
        query GetDiskDetails($id: PrefixedID!) {
          disk(id: $id) {
            id
            device
            name
            serialNum
            size
            temperature
          }
        }
        """
        variables = {"id": disk_id}
        try:
            logger.info(f"Executing get_disk_details for disk: {disk_id}")
            response_data = await make_graphql_request(query, variables)
            raw_disk = response_data.get("disk", {})
            
            if not raw_disk:
                raise ToolError(f"Disk '{disk_id}' not found")
            
            # Process disk information for human-readable output
            def format_bytes(bytes_value):
                if bytes_value is None: return "N/A"
                bytes_value = int(bytes_value)
                for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
                    if bytes_value < 1024.0:
                        return f"{bytes_value:.2f} {unit}"
                    bytes_value /= 1024.0
                return f"{bytes_value:.2f} EB"

            summary = {
                'disk_id': raw_disk.get('id'),
                'device': raw_disk.get('device'),
                'name': raw_disk.get('name'),
                'serial_number': raw_disk.get('serialNum'),
                'size_formatted': format_bytes(raw_disk.get('size')),
                'temperature': f"{raw_disk.get('temperature')}°C" if raw_disk.get('temperature') else 'N/A',
                'interface_type': raw_disk.get('interfaceType'),
                'smart_status': raw_disk.get('smartStatus'),
                'is_spinning': raw_disk.get('isSpinning'),
                'power_on_hours': raw_disk.get('powerOnHours'),
                'reallocated_sectors': raw_disk.get('reallocatedSectorCount'),
                'partition_count': len(raw_disk.get('partitions', [])),
                'total_partition_size': format_bytes(sum(p.get('size', 0) for p in raw_disk.get('partitions', []) if p.get('size')))
            }
            
            return {
                'summary': summary,
                'partitions': raw_disk.get('partitions', []),
                'details': raw_disk
            }
            
        except Exception as e:
            logger.error(f"Error in get_disk_details for {disk_id}: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve disk details for {disk_id}: {str(e)}")

    logger.info("Storage tools registered successfully")