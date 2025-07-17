from mcp.server.fastmcp import Context
from typing import Dict, Any, Optional
from ._shared import _make_request, mcp


@mcp.tool()
def get_system_message(context: Context) -> str:
    """
    Retrieves the currently active system-wide message or banner.

    Returns:
        The system message as an HTML string.
    """
    return _make_request(context, "GET", "/v1/config/system-message")


@mcp.tool()
def set_system_message(
    context: Context,
    message: str,
    start_time: str,
    end_time: str,
    delete_on_restart: bool,
) -> Dict[str, Any]:
    """
    Sets or updates the system-wide message. This is an admin-only function.

    Args:
        context: The MCP context.
        message: The message content, which can include HTML.
        start_time: The time for the message to start appearing, in ISO 8601 format (e.g., "2025-07-18T09:00:00Z").
        end_time: The time for the message to stop appearing, in ISO 8601 format.
        delete_on_restart: If True, the message will be cleared when the server restarts.

    Returns:
        A success message upon completion.
    """
    payload = {
        "message": message,
        "start": start_time,
        "end": end_time,
        "deleteOnRestart": delete_on_restart,
    }
    return _make_request(context, "POST", "/v1/config/system-message", json_data=payload)


@mcp.tool()
def get_server_property(context: Context, property_name: str) -> Dict[str, Any]:
    """
    Retrieves the value of a specific server configuration property.

    Args:
        context: The MCP context.
        property_name: The name of the property to retrieve (e.g., 'database.vendor').

    Returns:
        A dictionary containing the property's value.
    """
    return _make_request(context, "GET", f"/v1/config/property/{property_name}")


@mcp.tool()
def get_gator_version(context: Context) -> Dict[str, Any]:
    """
    Gets the current version of the GenePattern server.

    Returns:
        A dictionary containing the version string.
    """
    return _make_request(context, "GET", "/v1/config/gp-version")


@mcp.tool()
def get_current_user_id(context: Context) -> Dict[str, Any]:
    """
    Gets the user ID of the currently authenticated user.

    Returns:
        A dictionary containing the user ID.
    """
    return _make_request(context, "GET", "/v1/config/user")


@mcp.tool()
def is_admin(context: Context) -> Dict[str, Any]:
    """
    Checks if the currently authenticated user is an administrator.

    Returns:
        A dictionary with a boolean 'result' indicating admin status.
    """
    return _make_request(context, "GET", "/v1/config/admin")


@mcp.tool()
def check_is_admin(context: Context) -> str:
    """
    Checks if the current user is an administrator by attempting to access an admin-only endpoint.
    A successful call confirms admin privileges. The request will fail if the user is not an admin.

    Returns:
        A success message if the user is an admin.
    """
    return _make_request(context, "GET", "/v1/config/is-admin")


@mcp.tool()
def get_gator_url(context: Context) -> Dict[str, Any]:
    """
    Gets the public URL of the GenePattern server.

    Returns:
        A dictionary containing the server's URL.
    """
    return _make_request(context, "GET", "/v1/config/gp-url")
