from mcp.server.fastmcp import Context
from typing import Dict, Any
from ._shared import _make_request, mcp


@mcp.tool()
def get_user_summary(context: Context, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Gets a summary of user activity between a start and end date.
    Corresponds to WADL id='userSummary' at '/v1/usagestats/user_summary/{startDate}/{endDate}'.
    """
    path = f"/v1/usagestats/user_summary/{start_date}/{end_date}"
    return _make_request(context, "GET", path)


@mcp.tool()
def log_client_message(context: Context, logname: str, loglevel: str, message: str) -> Dict[str, Any]:
    """
    Logs a message from a client application.
    Corresponds to WADL id='userSummary' at '/v1/usagelogging/log'.
    """
    params = {"logname": logname, "loglevel": loglevel, "message": message}
    return _make_request(context, "GET", "/v1/usagelogging/log", params=params)


# -----------------------------------------------------------------------------
## System Configuration
# -----------------------------------------------------------------------------

@mcp.tool()
def get_system_message(context: Context) -> str:
    """Gets the current system message."""
    return _make_request(context, "GET", "/v1/config/system-message", extra_headers={"Accept": "text/html"})


@mcp.tool()
def set_system_message(context: Context, message: str) -> Dict[str, Any]:
    """Sets the system message. Requires admin privileges."""
    return _make_request(context, "POST", "/v1/config/system-message", data=message,
                         extra_headers={"Content-Type": "text/html"})


@mcp.tool()
def get_property(context: Context, prop: str) -> Dict[str, Any]:
    """Gets a specific server configuration property."""
    return _make_request(context, "GET", f"/v1/config/property/{prop}")


@mcp.tool()
def get_gene_pattern_version(context: Context) -> Dict[str, Any]:
    """Gets the GenePattern server version."""
    return _make_request(context, "GET", "/v1/config/gp-version")


@mcp.tool()
def get_config_user(context: Context) -> Dict[str, Any]:
    """
    Gets information about the current authenticated user.
    Corresponds to WADL id='getUser' at '/v1/config/user'.
    """
    return _make_request(context, "GET", "/v1/config/user")


@mcp.tool()
def is_admin(context: Context) -> Dict[str, Any]:
    """Checks if the current user is an administrator."""
    return _make_request(context, "GET", "/v1/config/admin")