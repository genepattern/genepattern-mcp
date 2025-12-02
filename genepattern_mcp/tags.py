from mcp.server.fastmcp import Context
from typing import Dict, Any, List, Optional
from ._shared import _make_request, mcp


def _get_base_lsid(full_lsid: str) -> str:
    """
    Extracts the base LSID (without version number) from a full LSID.

    For example:
    urn:lsid:broad.mit.edu:cancer.software.genepattern.module.analysis:00002:2
    becomes:
    urn:lsid:broad.mit.edu:cancer.software.genepattern.module.analysis:00002

    Args:
        full_lsid: The full LSID including version number

    Returns:
        The base LSID without the version number
    """
    # Split by colon and remove the last part (version number)
    parts = full_lsid.rsplit(':', 1)
    return parts[0]


@mcp.tool()
def get_all_tags(context: Context) -> List[Any]:
    """
    Retrieves a list of all job tags created by the current user.

    The response is a JSON array of tag objects, each with a 'value' key.
    Example: [{"value": "important"}, {"value": "rna-seq"}]
    """
    return _make_request(context, "GET", "/v1/tags")


# REMOVED: Due to this being geared towards UI functionality, and potential confusion with LSIDs
#
# @mcp.tool()
# def pin_module(
#     context: Context,
#     user: str,
#     position: int,
#     lsid: Optional[str] = None,
#     module_name: Optional[str] = None
# ) -> Dict[str, Any]:
#     """
#     Pins a module to the user's 'Favorites' tag at a specific position.
#
#     This tool accepts either an LSID or a module name. If a module name is provided,
#     it will automatically look up the correct LSID before pinning the module.
#     This prevents issues with hallucinated LSIDs.
#
#     Note: This endpoint requires the base LSID (without version number).
#     The version number will be automatically removed if present.
#
#     Args:
#         context: The MCP context.
#         user: The ID of the user for whom the module is being pinned.
#         position: The position (as an int) at which to pin the module.
#         lsid: The Life Science Identifier (LSID) of the module to pin. Either lsid or module_name must be provided.
#         module_name: The name of the module to pin. Either lsid or module_name must be provided.
#     """
#     # Validate that either lsid or module_name is provided
#     if not lsid and not module_name:
#         raise ValueError("Either 'lsid' or 'module_name' must be provided.")
#
#     if lsid and module_name:
#         raise ValueError("Only one of 'lsid' or 'module_name' should be provided, not both.")
#
#     # If module_name is provided, look up the LSID
#     lsid_to_use = lsid
#     if module_name:
#         task_details = _make_request(
#             context,
#             "GET",
#             f"/v1/tasks/{module_name}",
#             params={"includeProperties": False, "includeChildren": False, "includeEula": False,
#                    "includeSupportFiles": False, "includeParamGroups": False, "includeMemorySettings": False}
#         )
#
#         if not task_details or "lsid" not in task_details:
#             raise ValueError(f"Could not find LSID for module '{module_name}'. Please verify the module name is correct.")
#
#         lsid_to_use = task_details["lsid"]
#
#     # Extract base LSID (without version number)
#     base_lsid = _get_base_lsid(lsid_to_use)
#
#     payload = {"user": user, "lsid": base_lsid, "position": position}
#     return _make_request(context, "POST", "/v1/tags/pin", json_data=payload)


# REMOVED: Due to this being geared towards UI functionality, and potential confusion with LSIDs
#
# @mcp.tool()
# def repin_module(
#     context: Context,
#     user: str,
#     position: int,
#     lsid: Optional[str] = None,
#     module_name: Optional[str] = None
# ) -> Dict[str, Any]:
#     """
#     Moves an already pinned module to a new position in the user's 'Favorites'.
#
#     This tool accepts either an LSID or a module name. If a module name is provided,
#     it will automatically look up the correct LSID before repinning the module.
#     This prevents issues with hallucinated LSIDs.
#
#     Note: This endpoint requires the base LSID (without version number).
#     The version number will be automatically removed if present.
#
#     Args:
#         context: The MCP context.
#         user: The ID of the user.
#         position: The new position (as an int) for the pinned module.
#         lsid: The LSID of the module to move. Either lsid or module_name must be provided.
#         module_name: The name of the module to move. Either lsid or module_name must be provided.
#     """
#     # Validate that either lsid or module_name is provided
#     if not lsid and not module_name:
#         raise ValueError("Either 'lsid' or 'module_name' must be provided.")
#
#     if lsid and module_name:
#         raise ValueError("Only one of 'lsid' or 'module_name' should be provided, not both.")
#
#     # If module_name is provided, look up the LSID
#     lsid_to_use = lsid
#     if module_name:
#         task_details = _make_request(
#             context,
#             "GET",
#             f"/v1/tasks/{module_name}",
#             params={"includeProperties": False, "includeChildren": False, "includeEula": False,
#                    "includeSupportFiles": False, "includeParamGroups": False, "includeMemorySettings": False}
#         )
#
#         if not task_details or "lsid" not in task_details:
#             raise ValueError(f"Could not find LSID for module '{module_name}'. Please verify the module name is correct.")
#
#         lsid_to_use = task_details["lsid"]
#
#     # Extract base LSID (without version number)
#     base_lsid = _get_base_lsid(lsid_to_use)
#
#     payload = {"user": user, "lsid": base_lsid, "position": position}
#     return _make_request(context, "PUT", "/v1/tags/repin", json_data=payload)


@mcp.tool()
def unpin_module(context: Context, user: str, lsid: str) -> Dict[str, Any]:
    """
    Unpins a module, removing it from the user's 'Favorites'.

    Args:
        context: The MCP context.
        user: The ID of the user.
        lsid: The LSID of the module to unpin.
    """
    # The Java backend requires the position field in the JSON, even though it's not used.
    payload = {"user": user, "lsid": lsid, "position": 0.0}
    return _make_request(context, "DELETE", "/v1/tags/unpin", json_data=payload)