from mcp.server.fastmcp import Context
from typing import Dict, Any
from ._shared import _make_request, mcp


@mcp.tool()
def get_user_summary_stats(context: Context, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Retrieves a JSON object with summary data about server usage for a given date range.

    This is an admin-only function. It provides statistics such as new user registrations,
    job counts, CPU time, module execution counts, and more.

    Args:
        context: The MCP context.
        start_date: The start date for the summary report, in 'YYYY-MM-DD' format.
        end_date: The end date for the summary report, in 'YYYY-MM-DD' format.

    Returns:
        A dictionary containing a comprehensive summary of usage statistics.
    """
    return _make_request(context, "GET", f"/v1/usagestats/user_summary/{start_date}/{end_date}")