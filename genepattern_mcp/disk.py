from mcp.server.fastmcp import Context
from typing import Dict, Any, Optional
from ._shared import _make_request, mcp


@mcp.tool()
def get_disk_info(context: Context) -> Dict[str, Any]:
    """
    Retrieves the disk usage, quota, and job limit information for the current user.

    This includes details about file storage usage, job processing limits,
    and whether any quotas have been exceeded.

    Returns:
        A dictionary containing detailed disk and job quota information.
    """
    return _make_request(context, "GET", "/v1/disk")


@mcp.tool()
def notify_max_jobs_exceeded(context: Context, task_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Triggers a notification that the user has exceeded their maximum simultaneous job limit.

    This endpoint is typically called by the client to inform the server to send
    an email notification to the user and/or system administrators.

    Args:
        context: The MCP context.
        task_name: The name of the task that was being run when the limit was exceeded.

    Returns:
        The user's current disk and job quota information after sending the notification.
    """
    params = {"taskName": task_name}
    return _make_request(context, "POST", "/v1/disk/notifyMaxJobsExceeded", params=params)
