from mcp.server.fastmcp import Context
from typing import Dict, Any
from ._shared import _make_request, mcp


@mcp.tool()
def rename_file(context: Context, path: str, name: str) -> Dict[str, Any]:
    """Renames a file or directory on the server."""
    params = {"path": path, "name": name}
    return _make_request(context, "PUT", "/v1/data/rename", params=params)


@mcp.tool()
def create_directory(context: Context, path: str) -> Dict[str, Any]:
    """Creates a new directory at the specified path."""
    return _make_request(context, "PUT", f"/v1/data/createDirectory/{path}")


@mcp.tool()
def delete_file_or_directory(context: Context, path: str) -> Dict[str, Any]:
    """Deletes a file or directory from the server."""
    return _make_request(context, "DELETE", f"/v1/data/delete/{path}")


@mcp.tool()
def copy_file(context: Context, source: str, destination: str) -> Dict[str, Any]:
    """Copies a file from a source path to a destination path."""
    params = {"from": source, "to": destination}
    return _make_request(context, "POST", "/v1/data/copy", params=params)


@mcp.tool()
def move_file(context: Context, source: str, destination: str) -> Dict[str, Any]:
    """Moves a file from a source path to a destination path."""
    params = {"from": source, "to": destination}
    return _make_request(context, "PUT", "/v1/data/move", params=params)


@mcp.tool()
def get_user_files(context: Context) -> Dict[str, Any]:
    """
    Lists the files for the current user.
    Corresponds to WADL id='getUser' at '/v1/data/user/files'.
    """
    return _make_request(context, "GET", "/v1/data/user/files")
