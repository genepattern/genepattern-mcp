from mcp.server.fastmcp import Context
from typing import Dict, Any
from ._shared import _make_request, mcp


@mcp.tool()
def get_all_tags(context: Context) -> Dict[str, Any]:
    """
    Retrieves a list of all job tags created by the current user.

    The response is a JSON array of tag objects, each with a 'value' key.
    Example: [{"value": "important"}, {"value": "rna-seq"}]
    """
    return _make_request(context, "GET", "/v1/tags")


@mcp.tool()
def pin_module(context: Context, user: str, lsid: str, position: float) -> Dict[str, Any]:
    """
    Pins a module to the user's 'Favorites' tag at a specific position.

    Args:
        context: The MCP context.
        user: The ID of the user for whom the module is being pinned.
        lsid: The Life Science Identifier (LSID) of the module to pin.
        position: The position (as a float) at which to pin the module.
    """
    payload = {"user": user, "lsid": lsid, "position": position}
    return _make_request(context, "POST", "/v1/tags/pin", json_data=payload)


@mcp.tool()
def repin_module(context: Context, user: str, lsid: str, position: float) -> Dict[str, Any]:
    """
    Moves an already pinned module to a new position in the user's 'Favorites'.

    Args:
        context: The MCP context.
        user: The ID of the user.
        lsid: The LSID of the module to move.
        position: The new position for the pinned module.
    """
    payload = {"user": user, "lsid": lsid, "position": position}
    return _make_request(context, "PUT", "/v1/tags/repin", json_data=payload)


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