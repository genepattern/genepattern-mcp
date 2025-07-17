from mcp.server.fastmcp import Context
from typing import Dict, Any, Optional, List
from ._shared import _make_request, mcp


# ------------------------------------------------------------------------------
# Job Submission
# ------------------------------------------------------------------------------

@mcp.tool()
def add_job(context: Context, job_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Submits a new job or a batch of jobs to the server.

    Args:
        context: The MCP context.
        job_payload: A dictionary representing the job submission JSON.
            Example structure:
            {
                "lsid": "urn:lsid:broad.mit.edu:cancer.software.genepattern.module.analysis:00020:4",
                "params": [
                    {
                        "name": "input.filename",
                        "values": ["ftp://ftp.broadinstitute.org/pub/genepattern/datasets/all_aml/all_aml_test.gct"]
                    },
                    {
                        "name": "output.filename",
                        "values": ["all_aml_test.preprocessed.gct"]
                    }
                ],
                "tags": ["analysis", "preprocessing"]
            }
            For batch jobs, include "batchParam": True within a parameter object.
            For file groups, include "groupId": "group_name" within a parameter object.
    """
    return _make_request(context, "POST", "/v1/jobs", json_data=job_payload)


# ------------------------------------------------------------------------------
# Job Information & Search
# ------------------------------------------------------------------------------

@mcp.tool()
def search_jobs(
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
) -> Dict[str, Any]:
    """
    Searches for jobs based on a wide range of criteria.

    Args:
        context: The MCP context.
        user_id: Filter by user ID.
        group_id: Filter by group ID.
        batch_id: Filter by batch ID.
        tag: Filter by a specific tag.
        comment: Filter by text within a job's comment.
        module: Filter by module name.
        page: The page number for paginated results (1-based).
        page_size: The number of results per page.
        order_by: Field to order jobs by (e.g., 'jobId', '-dateSubmitted').
        order_files_by: Field to order a job's output files by (e.g., 'name', '-size').
        include_children: Whether to include child jobs in the response for pipelines.
        include_input_params: Whether to include detailed input parameters for each job.
        include_output_files: Whether to include the list of output files for each job.
        include_permissions: Whether to include permissions for each job.
    """
    params = locals()
    params.pop("context")
    # Convert camelCase and filter out None values
    final_params = {
        "userId": params.pop("user_id"),
        "groupId": params.pop("group_id"),
        "batchId": params.pop("batch_id"),
        "pageSize": params.pop("page_size"),
        "orderBy": params.pop("order_by"),
        "orderFilesBy": params.pop("order_files_by"),
        "includeChildren": params.pop("include_children"),
        "includeInputParams": params.pop("include_input_params"),
        "includeOutputFiles": params.pop("include_output_files"),
        "includePermissions": params.pop("include_permissions"),
        **params,
    }
    return _make_request(context, "GET", "/v1/jobs", params={k: v for k, v in final_params.items() if v is not None})


@mcp.tool()
def get_job_details(
    context: Context,
    job_id: str,
    include_permissions: bool = False,
    include_children: bool = True,
    include_input_params: bool = False,
    include_output_files: bool = True,
) -> Dict[str, Any]:
    """
    Retrieves a detailed JSON representation for a single job.

    Args:
        context: The MCP context.
        job_id: The ID of the job to retrieve.
        include_permissions: Whether to include job permissions.
        include_children: For pipelines, whether to include child jobs.
        include_input_params: Whether to include detailed input parameters.
        include_output_files: Whether to include the list of output files.
    """
    params = {
        "includePermissions": include_permissions,
        "includeChildren": include_children,
        "includeInputParams": include_input_params,
        "includeOutputFiles": include_output_files,
    }
    return _make_request(context, "GET", f"/v1/jobs/{job_id}", params=params)


@mcp.tool()
def get_job_status(context: Context, job_id: str) -> Dict[str, Any]:
    """
    Gets the status object for a single job.

    Args:
        context: The MCP context.
        job_id: The ID of the job.
    """
    return _make_request(context, "GET", f"/v1/jobs/{job_id}/status.json")


@mcp.tool()
def get_multiple_job_statuses(context: Context, job_ids: List[str]) -> Dict[str, Any]:
    """
    Gets status objects for multiple jobs in a single request.

    Args:
        context: The MCP context.
        job_ids: A list of job IDs to query.
    """
    return _make_request(context, "GET", "/v1/jobs/jobstatus.json", params={"jobId": job_ids})


@mcp.tool()
def get_recent_jobs(
    context: Context,
    include_children: bool = True,
    include_input_params: bool = False,
    include_output_files: bool = True,
) -> Dict[str, Any]:
    """
    Retrieves a list of the current user's most recent jobs.

    Args:
        context: The MCP context.
        include_children: Whether to include child jobs for pipelines.
        include_input_params: Whether to include detailed input parameters.
        include_output_files: Whether to include the list of output files.
    """
    params = {
        "includeChildren": include_children,
        "includeInputParams": include_input_params,
        "includeOutputFiles": include_output_files,
    }
    return _make_request(context, "GET", "/v1/jobs/recent", params=params)


@mcp.tool()
def get_incomplete_jobs(context: Context) -> Dict[str, Any]:
    """
    Returns a list of job numbers for the current user's pending or running jobs.
    """
    return _make_request(context, "GET", "/v1/jobs/incomplete")


@mcp.tool()
def get_job_children(
    context: Context, job_id: str, include_output_files: bool = True
) -> Dict[str, Any]:
    """
    For a pipeline job, retrieves a list of its child jobs.

    Args:
        context: The MCP context.
        job_id: The ID of the parent pipeline job.
        include_output_files: Whether to include output files for each child job.
    """
    params = {"includeOutputFiles": include_output_files}
    return _make_request(context, "GET", f"/v1/jobs/{job_id}/children", params=params)


# ------------------------------------------------------------------------------
# Job Management & Actions
# ------------------------------------------------------------------------------

@mcp.tool()
def terminate_job(context: Context, job_id: str) -> Dict[str, Any]:
    """
    Terminates a running job.

    Args:
        context: The MCP context.
        job_id: The ID of the job to terminate.
    """
    return _make_request(context, "DELETE", f"/v1/jobs/{job_id}/terminate")


@mcp.tool()
def delete_job(context: Context, job_id: str) -> Dict[str, Any]:
    """
    Deletes a job from the server.

    Args:
        context: The MCP context.
        job_id: The ID of the job to delete.
    """
    return _make_request(context, "DELETE", f"/v1/jobs/{job_id}/delete")


@mcp.tool()
def delete_jobs(context: Context, job_ids: List[str]) -> Dict[str, Any]:
    """
    Deletes a list of jobs from the server.

    Args:
        context: The MCP context.
        job_ids: A list of job IDs to delete.
    """
    params = {"jobs": ",".join(job_ids)}
    return _make_request(context, "DELETE", "/v1/jobs/delete", params=params)


@mcp.tool()
def get_job_permissions(context: Context, job_id: str) -> Dict[str, Any]:
    """
    Gets the permissions for a job, including groups it can be shared with.

    Args:
        context: The MCP context.
        job_id: The ID of the job.
    """
    return _make_request(context, "GET", f"/v1/jobs/{job_id}/permissions")


@mcp.tool()
def set_job_permissions(context: Context, job_id: str, permissions_payload: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Sets the permissions for a job.

    Args:
        context: The MCP context.
        job_id: The ID of the job.
        permissions_payload: A list of permission objects.
            Example: [{"id": "GROUP_NAME", "read": True, "write": False}]
    """
    return _make_request(context, "PUT", f"/v1/jobs/{job_id}/permissions", json_data=permissions_payload)


@mcp.tool()
def add_job_tag(context: Context, job_id: int, tag_text: str) -> Dict[str, Any]:
    """
    Adds a tag to a specified job.

    Args:
        context: The MCP context.
        job_id: The job number.
        tag_text: The text of the tag to add.
    """
    return _make_request(context, "POST", f"/v1/jobs/{job_id}/tags/add", params={"tagText": tag_text})


@mcp.tool()
def delete_job_tag(context: Context, job_id: int, job_tag_id: int) -> Dict[str, Any]:
    """
    Deletes a specific tag from a job.

    Args:
        context: The MCP context.
        job_id: The job number.
        job_tag_id: The ID of the job-tag association to delete.
    """
    return _make_request(context, "POST", f"/v1/jobs/{job_id}/tags/delete", params={"jobTagId": job_tag_id})

# ------------------------------------------------------------------------------
# Job-related Utilities
# ------------------------------------------------------------------------------

@mcp.tool()
def download_job_results(context: Context, job_id: str) -> Dict[str, Any]:
    """
    Downloads the result files of a job as a zip archive.

    Args:
        context: The MCP context.
        job_id: The ID of the job.
    """
    return _make_request(context, "GET", f"/v1/jobs/{job_id}/download")


@mcp.tool()
def get_job_code_example(context: Context, job_id: str, language: str) -> Dict[str, Any]:
    """
    Generates and retrieves example code to reproduce a given job.

    Args:
        context: The MCP context.
        job_id: The ID of the job.
        language: The programming language for the code (e.g., 'Java', 'Python', 'R').
    """
    return _make_request(context, "GET", f"/v1/jobs/{job_id}/code", params={"language": language})


@mcp.tool()
def get_visualizer_input_files(context: Context, job_id: int) -> Dict[str, Any]:
    """
    Gets a list of input file URLs for a visualizer job.

    Args:
        context: The MCP context.
        job_id: The ID of the visualizer job.
    """
    return _make_request(context, "GET", f"/v1/jobs/{job_id}/visualizerInputFiles")


@mcp.tool()
def get_visualizer_command_line(context: Context, job_id: int, commandline: str) -> Dict[str, Any]:
    """
    Gets a visualizer's command line with input file parameters substituted.

    Args:
        context: The MCP context.
        job_id: The ID of the visualizer job.
        commandline: The unsubstituted command line template string.
    """
    params = {"commandline": commandline}
    return _make_request(context, "GET", f"/v1/jobs/{job_id}/visualizerCmdLine", params=params)
