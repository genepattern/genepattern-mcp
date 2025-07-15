from mcp.server.fastmcp import Context
from typing import Dict, Any, Optional
from ._shared import _make_request, mcp


@mcp.tool()
def get_all_tasks(context: Context, include_hidden: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves a list of all available tasks (modules)."""
    params = {"includeHidden": include_hidden}
    return _make_request(context, "GET", "/v1/tasks/all.json", params=params)


@mcp.tool()
def get_task(
        context: Context,
        task_name_or_lsid: str,
        include_properties: bool = True,
        include_children: bool = True,
        include_eula: bool = True,
        include_support_files: bool = True,
        include_param_groups: bool = True,
        include_memory_settings: bool = True,
) -> Dict[str, Any]:
    """Gets detailed information for a specific task."""
    path = f"/v1/tasks/{task_name_or_lsid}"
    params = {
        "includeProperties": include_properties, "includeChildren": include_children,
        "includeEula": include_eula, "includeSupportFiles": include_support_files,
        "includeParamGroups": include_param_groups, "includeMemorySettings": include_memory_settings,
    }
    return _make_request(context, "GET", path, params=params)


@mcp.tool()
def get_task_manifest(context: Context, task_name_or_lsid: str) -> Any:
    """Retrieves the manifest file for a given task."""
    return _make_request(context, "GET", f"/v1/tasks/{task_name_or_lsid}/manifest")