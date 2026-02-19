"""Virtual machine management.

Provides the `unraid_vm` tool with 9 actions for VM lifecycle management
including start, stop, pause, resume, force stop, reboot, and reset.
"""

from typing import Any, Literal, get_args

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError, tool_error_handler


QUERIES: dict[str, str] = {
    "list": """
        query ListVMs {
          vms { id domains { id name state uuid } }
        }
    """,
    # NOTE: The Unraid GraphQL API does not expose a single-VM query.
    # The details query is identical to list; client-side filtering is required.
    "details": """
        query ListVMs {
          vms { id domains { id name state uuid } }
        }
    """,
}

MUTATIONS: dict[str, str] = {
    "start": """
        mutation StartVM($id: PrefixedID!) { vm { start(id: $id) } }
    """,
    "stop": """
        mutation StopVM($id: PrefixedID!) { vm { stop(id: $id) } }
    """,
    "pause": """
        mutation PauseVM($id: PrefixedID!) { vm { pause(id: $id) } }
    """,
    "resume": """
        mutation ResumeVM($id: PrefixedID!) { vm { resume(id: $id) } }
    """,
    "force_stop": """
        mutation ForceStopVM($id: PrefixedID!) { vm { forceStop(id: $id) } }
    """,
    "reboot": """
        mutation RebootVM($id: PrefixedID!) { vm { reboot(id: $id) } }
    """,
    "reset": """
        mutation ResetVM($id: PrefixedID!) { vm { reset(id: $id) } }
    """,
}

# Map action names to GraphQL field names (only where they differ)
_MUTATION_FIELDS: dict[str, str] = {
    "force_stop": "forceStop",
}

DESTRUCTIVE_ACTIONS = {"force_stop", "reset"}

VM_ACTIONS = Literal[
    "list",
    "details",
    "start",
    "stop",
    "pause",
    "resume",
    "force_stop",
    "reboot",
    "reset",
]

ALL_ACTIONS = set(QUERIES) | set(MUTATIONS)

if set(get_args(VM_ACTIONS)) != ALL_ACTIONS:
    _missing = ALL_ACTIONS - set(get_args(VM_ACTIONS))
    _extra = set(get_args(VM_ACTIONS)) - ALL_ACTIONS
    raise RuntimeError(
        f"VM_ACTIONS and ALL_ACTIONS are out of sync. "
        f"Missing from Literal: {_missing or 'none'}. Extra in Literal: {_extra or 'none'}"
    )


def register_vm_tool(mcp: FastMCP) -> None:
    """Register the unraid_vm tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_vm(
        action: VM_ACTIONS,
        vm_id: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Manage Unraid virtual machines.

        Actions:
          list - List all VMs with state
          details - Detailed info for a VM (requires vm_id: UUID, PrefixedID, or name)
          start - Start a VM (requires vm_id)
          stop - Gracefully stop a VM (requires vm_id)
          pause - Pause a VM (requires vm_id)
          resume - Resume a paused VM (requires vm_id)
          force_stop - Force stop a VM (requires vm_id, confirm=True)
          reboot - Reboot a VM (requires vm_id)
          reset - Reset a VM (requires vm_id, confirm=True)
        """
        if action not in ALL_ACTIONS:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(ALL_ACTIONS)}")

        if action != "list" and not vm_id:
            raise ToolError(f"vm_id is required for '{action}' action")

        if action in DESTRUCTIVE_ACTIONS and not confirm:
            raise ToolError(f"Action '{action}' is destructive. Set confirm=True to proceed.")

        with tool_error_handler("vm", action, logger):
            try:
                logger.info(f"Executing unraid_vm action={action}")

                if action == "list":
                    data = await make_graphql_request(QUERIES["list"])
                    if data.get("vms"):
                        vms = data["vms"].get("domains") or data["vms"].get("domain") or []
                        if isinstance(vms, dict):
                            vms = [vms]
                        return {"vms": vms}
                    return {"vms": []}

                if action == "details":
                    data = await make_graphql_request(QUERIES["details"])
                    if not data.get("vms"):
                        raise ToolError("No VM data returned from server")
                    vms = data["vms"].get("domains") or data["vms"].get("domain") or []
                    if isinstance(vms, dict):
                        vms = [vms]
                    for vm in vms:
                        if (
                            vm.get("uuid") == vm_id
                            or vm.get("id") == vm_id
                            or vm.get("name") == vm_id
                        ):
                            return dict(vm)
                    available = [f"{v.get('name')} (UUID: {v.get('uuid')})" for v in vms]
                    raise ToolError(f"VM '{vm_id}' not found. Available: {', '.join(available)}")

                # Mutations
                if action in MUTATIONS:
                    data = await make_graphql_request(MUTATIONS[action], {"id": vm_id})
                    field = _MUTATION_FIELDS.get(action, action)
                    if data.get("vm") and field in data["vm"]:
                        return {
                            "success": data["vm"][field],
                            "action": action,
                            "vm_id": vm_id,
                        }
                    raise ToolError(f"Failed to {action} VM or unexpected response")

                raise ToolError(f"Unhandled action '{action}' — this is a bug")

            except ToolError:
                raise
            except Exception as e:
                if "VMs are not available" in str(e):
                    raise ToolError(
                        "VMs not available on this server. Check VM support is enabled."
                    ) from e
                raise

    logger.info("VM tool registered successfully")
