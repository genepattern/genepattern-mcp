from mcp.server.fastmcp import Context
from typing import Dict, Any, Optional
from ._shared import _make_request, mcp


@mcp.tool()
def rename_file(context: Context, path: str, name: str) -> Dict[str, Any]:
    """
    Renames a file or directory in the user's upload space.
    This operation is only implemented for files and directories within the '/users/{user_id}/' path.

    Args:
        context: The MCP context.
        path: The full path to the file or directory to rename (e.g., '/users/my_user/data.txt').
        name: The new name for the file or directory.
    """
    params = {"path": path, "name": name}
    return _make_request(context, "PUT", "/v1/data/rename", params=params)

# ------------------------------------------------------------------------------

@mcp.tool()
def create_directory(context: Context, path: str) -> Dict[str, Any]:
    """
    Creates a new directory in the user's upload space.
    This operation is not recursive; the parent directory must already exist.

    Args:
        context: The MCP context.
        path: The path for the new directory, relative to the user's upload root (e.g., 'new_folder/sub_folder').
    """
    return _make_request(context, "PUT", f"/v1/data/createDirectory/{path}")

# ------------------------------------------------------------------------------

@mcp.tool()
def delete_file_or_directory(context: Context, path: str) -> Dict[str, Any]:
    """
    Deletes a file or directory.
    Supports deleting from the user's upload space (e.g., '/users/my_user/data.txt') or from job results (e.g., '/jobResults/123/output.txt').

    Args:
        context: The MCP context.
        path: The full path to the file or directory to delete.
    """
    return _make_request(context, "DELETE", f"/v1/data/delete/{path}")

# ------------------------------------------------------------------------------

@mcp.tool()
def copy_file(context: Context, source: str, destination: str) -> Dict[str, Any]:
    """
    Copies a file from a source path to a destination path in the user's upload space.
    The source can be a user-uploaded file or a job result file. The destination must be in the user's upload space.

    Args:
        context: The MCP context.
        source: The full path of the file to copy (e.g., '/jobResults/123/output.txt').
        destination: The full destination path in the user's upload space (e.g., '/users/my_user/copied_file.txt').
    """
    params = {"from": source, "to": destination}
    return _make_request(context, "POST", "/v1/data/copy", params=params)

# ------------------------------------------------------------------------------

@mcp.tool()
def move_file(context: Context, source: str, destination: str) -> Dict[str, Any]:
    """
    Moves a file or directory to a new location in the user's upload space.
    The source can be a user-uploaded item or a job result. The destination must be in the user's upload space.
    Cannot move a directory into itself or a child of itself.

    Args:
        context: The MCP context.
        source: The full path of the file or directory to move (e.g., '/users/my_user/old_data.txt').
        destination: The full destination path (e.g., '/users/my_user/archive/new_data.txt').
    """
    params = {"from": source, "to": destination}
    return _make_request(context, "PUT", "/v1/data/move", params=params)

# ------------------------------------------------------------------------------

@mcp.tool()
def get_user_files(context: Context) -> Dict[str, Any]:
    """
    Retrieves a JSON representation of the file and directory structure in the current user's upload space,
    similar to what is displayed in the 'Files' tab.
    """
    return _make_request(context, "GET", "/v1/data/user/files")

# ------------------------------------------------------------------------------

@mcp.tool()
def download_item(context: Context, path: str) -> Dict[str, Any]:
    """
    Downloads a file or directory. Currently, only directory downloads are implemented,
    which are returned as a zip archive. Single file downloads should use the DataServlet.

    Args:
        context: The MCP context.
        path: The path to the directory to download (e.g., '/users/my_user/my_folder').
    """
    params = {"path": path}
    return _make_request(context, "GET", "/v1/data/download", params=params)

# ------------------------------------------------------------------------------

@mcp.tool()
def upload_file(
    context: Context, path: str, file_content: bytes, replace: bool = False
) -> Dict[str, Any]:
    """
    Uploads a file to a specified path in the user's upload directory.
    The file content is sent as the raw request body.

    Args:
        context: The MCP context.
        path: The destination path for the file, relative to the user's upload root (e.g., 'new_data.txt' or 'folder/new_data.txt').
        file_content: The raw byte content of the file to upload.
        replace: If True, overwrite the file if it already exists. Defaults to False.
    """
    params = {"replace": replace}
    return _make_request(context, "PUT", f"/v1/data/upload/{path}", params=params, data=file_content)

# ------------------------------------------------------------------------------

@mcp.tool()
def upload_job_input_from_body(
    context: Context, name: str, file_content: bytes
) -> Dict[str, Any]:
    """
    Uploads a file to be used as a job input. The file content is sent as the raw request body,
    and the filename is specified as a query parameter. The file is stored in a temporary location.

    Args:
        context: The MCP context.
        name: The name of the file being uploaded.
        file_content: The raw byte content of the file.
    """
    params = {"name": name}
    return _make_request(context, "POST", "/v1/data/upload/job_input", params=params, data=file_content)

# ------------------------------------------------------------------------------

@mcp.tool()
def upload_job_input_from_form(
    context: Context, file_content: bytes, file_name: str
) -> Dict[str, Any]:
    """
    Uploads a file from a multipart form to be used as a job input.
    This method creates a new resource and is an alternative to sending raw file data in the request body.

    Args:
        context: The MCP context.
        file_content: The raw byte content of the file.
        file_name: The name to assign to the file in the form data.
    """
    files = {"file": (file_name, file_content)}
    return _make_request(context, "POST", "/v1/data/upload/job_input_form", files=files)

# ------------------------------------------------------------------------------

@mcp.tool()
def upload_job_output(
    context: Context, name: str, jobid: str, file_content: bytes
) -> Dict[str, Any]:
    """
    Uploads a file to be associated as an output file for a specific job.
    The user must have write permissions for the target job.

    Args:
        context: The MCP context.
        name: The name to give the output file.
        jobid: The ID of the job to associate the file with.
        file_content: The raw byte content of the file.
    """
    params = {"name": name, "jobid": jobid}
    return _make_request(context, "POST", "/v1/data/upload/job_output", params=params, data=file_content)

# ------------------------------------------------------------------------------

@mcp.tool()
def create_pipeline(
    context: Context, path: str, name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Creates a provenance pipeline from a given job result file.

    Args:
        context: The MCP context.
        path: The path to the job result file to use for creating the pipeline (e.g., '/jobResults/123/output.gct').
        name: The name for the new pipeline. If not provided, a default name (e.g., 'job_123') will be generated.
    """
    params = {}
    if name:
        params["name"] = name
    return _make_request(context, "PUT", f"/v1/data/createPipeline/{path}", params=params)