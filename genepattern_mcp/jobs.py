from mcp.server.fastmcp import Context
from typing import Dict, Any, Optional
from ._shared import _make_request, mcp


@mcp.tool()
def get_job_search_results(
        context: Context,
        user_id: Optional[str] = None,
        group_id: Optional[str] = None,
        batch_id: Optional[str] = None,
        tag: Optional[str] = None,
        comment: Optional[str] = None,
        module: Optional[str] = None,
        page: int = 1,
        page_size: Optional[int] = None,
        order_by: Optional[str] = None,
        order_files_by: Optional[str] = None,
        include_children: bool = True,
        include_input_params: bool = False,
        include_output_files: bool = True,
        include_permissions: bool = True,
        pretty_print: bool = True,
) -> Dict[str, Any]:
    """Searches for jobs with a variety of filter criteria."""
    params = {
        "userId": user_id, "groupId": group_id, "batchId": batch_id, "tag": tag,
        "comment": comment, "module": module, "page": page, "pageSize": page_size,
        "orderBy": order_by, "orderFilesBy": order_files_by, "includeChildren": include_children,
        "includeInputParams": include_input_params, "includeOutputFiles": include_output_files,
        "includePermissions": include_permissions, "prettyPrint": pretty_print,
    }
    return _make_request(context, "GET", "/v1/jobs", params=params)


@mcp.tool()
def add_job(context: Context, job_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Submits a new job.
    Corresponds to WADL id='addJob' at '/v1/jobs'.
    """
    return _make_request(context, "POST", "/v1/jobs", json_data=job_config)


@mcp.tool()
def get_job(
        context: Context,
        job_id: str,
        include_permissions: bool = False,
        include_children: bool = True,
        include_input_params: bool = False,
        include_output_files: bool = True,
        pretty_print: bool = True,
) -> Dict[str, Any]:
    """Retrieves the details for a specific job."""
    path = f"/v1/jobs/{job_id}"
    params = {
        "includePermissions": include_permissions, "includeChildren": include_children,
        "includeInputParams": include_input_params, "includeOutputFiles": include_output_files,
        "prettyPrint": pretty_print,
    }
    return _make_request(context, "GET", path, params=params)


@mcp.tool()
def get_job_status(context: Context, job_id: str) -> Dict[str, Any]:
    """Gets the status of a specific job."""
    return _make_request(context, "GET", f"/v1/jobs/{job_id}/status.json")


@mcp.tool()
def terminate_job(context: Context, job_id: str) -> Dict[str, Any]:
    """Terminates a running job."""
    return _make_request(context, "DELETE", f"/v1/jobs/{job_id}/terminate")


@mcp.tool()
def delete_job(context: Context, job_id: str) -> Dict[str, Any]:
    """Deletes a job from the server."""
    return _make_request(context, "DELETE", f"/v1/jobs/{job_id}/delete")


@mcp.tool()
def add_tag_to_job(context: Context, job_no: int, tag_text: str) -> Dict[str, Any]:
    """Adds a tag to a specific job."""
    path = f"/v1/jobs/{job_no}/tags/add"
    params = {"tagText": tag_text}
    return _make_request(context, "POST", path, params=params)