from mcp.server.fastmcp import Context
from typing import Dict, Any
from ._shared import _make_request, mcp


@mcp.tool()
def upload_file_from_path(context: Context, local_path: str, remote_path: str, replace: bool = False) -> Dict[str, Any]:
    """
    Uploads a local file to a specified path on the server.
    This corresponds to PUT /v1/data/upload/{path}
    """
    params = {"replace": replace}
    with open(local_path, 'rb') as f:
        data = f.read()

    headers = {"Content-Length": str(len(data))}
    return _make_request(context, "PUT", f"/v1/data/upload/{remote_path}", params=params, data=data,
                         extra_headers=headers)


@mcp.tool()
def upload_file_for_job_input(context: Context, local_file_path: str, file_name: str) -> Dict[str, Any]:
    """
    Uploads a file for a job input form.
    Corresponds to POST /v1/data/upload/job_input_form
    """
    with open(local_file_path, 'rb') as f:
        files = {'file': (file_name, f)}
        headers = {"Content-Length": str(len(f.read()))}  # Content-Length might be handled by requests
        return _make_request(context, "POST", "/v1/data/upload/job_input_form", files=files, extra_headers=headers)