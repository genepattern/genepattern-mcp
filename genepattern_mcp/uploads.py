from mcp.server.fastmcp import Context
from typing import Dict, Any, Optional
from ._shared import _make_request, mcp


# ------------------------------------------------------------------------------
# Standard Whole File Upload
# ------------------------------------------------------------------------------

@mcp.tool()
def upload_whole_file(
    context: Context, path: str, file_content: bytes
) -> Dict[str, Any]:
    """
    Uploads an entire file in a single POST request to a specified path in the user's upload directory.

    Args:
        context: The MCP context.
        path: The destination path for the file, relative to the user's upload root (e.g., 'data/my_file.txt').
        file_content: The raw byte content of the file to upload.
    """
    params = {"path": path}
    return _make_request(context, "POST", "/v1/upload/whole", params=params, data=file_content)

# ------------------------------------------------------------------------------
# Server-Side Chunked Upload
# ------------------------------------------------------------------------------

@mcp.tool()
def start_server_multipart_upload(
    context: Context, path: str, num_parts: int, file_size: int
) -> Dict[str, Any]:
    """
    Initializes a server-side multipart upload process and returns a unique token for the session.
    This is for chunked uploads directly to the GenePattern server.

    Args:
        context: The MCP context.
        path: The destination path for the file.
        num_parts: The total number of chunks the file will be broken into.
        file_size: The total size of the file in bytes.
    """
    params = {"path": path, "parts": num_parts, "fileSize": file_size}
    return _make_request(context, "POST", "/v1/upload/multipart/", params=params)


@mcp.tool()
def upload_server_multipart_chunk(
    context: Context, token: str, path: str, chunk_index: int, total_parts: int, chunk_data: bytes
) -> Dict[str, Any]:
    """
    Uploads a single chunk of a file for a server-side multipart upload session.

    Args:
        context: The MCP context.
        token: The upload token received from `start_server_multipart_upload`.
        path: The destination path for the final file.
        chunk_index: The 0-based index of the file chunk being uploaded.
        total_parts: The total number of chunks for the file.
        chunk_data: The raw byte content of the chunk.
    """
    params = {"token": token, "path": path, "index": chunk_index, "parts": total_parts}
    return _make_request(context, "PUT", "/v1/upload/multipart/", params=params, data=chunk_data)


@mcp.tool()
def get_server_multipart_status(
    context: Context, token: str, path: str, num_parts: int
) -> Dict[str, Any]:
    """
    Gets the status of a server-side multipart upload, returning lists of missing and received chunks.

    Args:
        context: The MCP context.
        token: The upload token for the session.
        path: The destination path for the file.
        num_parts: The total number of parts for the upload.
    """
    params = {"token": token, "path": path, "parts": num_parts}
    return _make_request(context, "GET", "/v1/upload/multipart/", params=params)


@mcp.tool()
def assemble_server_multipart_upload(
    context: Context, path: str, token: str, num_parts: int
) -> Dict[str, Any]:
    """
    Assembles the completed chunks of a server-side multipart upload into the final file and registers it.

    Args:
        context: The MCP context.
        path: The destination path for the final file.
        token: The upload token for the session.
        num_parts: The total number of parts for the upload.
    """
    params = {"path": path, "token": token, "parts": num_parts}
    return _make_request(context, "POST", "/v1/upload/multipart/assemble/", params=params)

# ------------------------------------------------------------------------------
# Direct-to-S3 Multipart Upload
# ------------------------------------------------------------------------------

@mcp.tool()
def start_s3_multipart_upload(
    context: Context, path: str, index: Optional[str] = None, param_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Initiates a multipart upload directly to an external S3 bucket and returns the UploadId.

    Args:
        context: The MCP context.
        path: The destination path for the file. If part of a job submission, this is just the filename.
        index: For job inputs, the 0-based index of the file parameter value.
        param_name: For job inputs, the name of the file parameter.
    """
    params = {"path": path}
    if index is not None:
        params["index"] = index
    if param_name:
        params["paramName"] = param_name
    return _make_request(context, "GET", "/v1/upload/startS3MultipartUpload/", params=params)


@mcp.tool()
def get_s3_presigned_url_for_part(
    context: Context, path: str, part_num: int, upload_id: str
) -> Dict[str, Any]:
    """
    Retrieves a pre-signed URL for uploading a single part of a file to S3.

    Args:
        context: The MCP context.
        path: The destination path for the file on the server.
        part_num: The part number (1-based) to get a URL for.
        upload_id: The ID of the multipart upload, returned by `start_s3_multipart_upload`.
    """
    params = {"path": path, "partNum": part_num, "uploadId": upload_id}
    return _make_request(context, "GET", "/v1/upload/getS3MultipartUploadPresignedUrlOnePart/", params=params)


@mcp.tool()
def register_external_upload(
    context: Context, path: str, length: int, upload_id: str, parts_payload: str
) -> Dict[str, Any]:
    """
    Completes a direct-to-S3 multipart upload and registers the file in GenePattern.

    Args:
        context: The MCP context.
        path: The destination path for the file.
        length: The total size of the file in bytes.
        upload_id: The ID of the multipart upload session.
        parts_payload: A plain text string containing a JSON array of the uploaded parts and their ETags.
                       Example: '[{"ETag": "\\"abc..."\\", "PartNumber": 1}, {"ETag": "\\"def..."\\", "PartNumber": 2}]'
    """
    params = {"path": path, "length": str(length), "uploadId": upload_id}
    headers = {"Content-Type": "text/plain"}
    return _make_request(context, "POST", "/v1/upload/registerExternalUpload", params=params, data=parts_payload, extra_headers=headers)

# ------------------------------------------------------------------------------
# Resumable.js Upload (specialized client)
# ------------------------------------------------------------------------------

@mcp.tool()
def check_resumable_chunk(
    context: Context,
    target_path: str,
    resumable_chunk_number: int,
    resumable_chunk_size: int,
    resumable_total_size: int,
    resumable_identifier: str,
    resumable_filename: str,
    resumable_relative_path: str,
) -> Dict[str, Any]:
    """
    Checks if a specific chunk for a resumable.js upload has already been received by the server.

    Args:
        context: The MCP context.
        target_path: The final destination path for the uploaded file.
        resumable_chunk_number: The 1-based index of the chunk to check.
        resumable_chunk_size: The size of each chunk in bytes.
        resumable_total_size: The total size of the file.
        resumable_identifier: A unique identifier for the file upload.
        resumable_filename: The name of the file.
        resumable_relative_path: The relative path of the file.
    """
    params = {
        "target": target_path,
        "resumableChunkNumber": resumable_chunk_number,
        "resumableChunkSize": resumable_chunk_size,
        "resumableTotalSize": resumable_total_size,
        "resumableIdentifier": resumable_identifier,
        "resumableFilename": resumable_filename,
        "resumableRelativePath": resumable_relative_path,
    }
    return _make_request(context, "GET", "/v1/upload/resumable/", params=params)


@mcp.tool()
def upload_resumable_chunk(
    context: Context,
    target_path: str,
    resumable_chunk_number: int,
    resumable_chunk_size: int,
    resumable_total_size: int,
    resumable_identifier: str,
    resumable_filename: str,
    resumable_relative_path: str,
    chunk_data: bytes,
) -> Dict[str, Any]:
    """
    Uploads a single chunk of a file using the resumable.js protocol.

    Args:
        context: The MCP context.
        target_path: The final destination path for the uploaded file.
        resumable_chunk_number: The 1-based index of the chunk being uploaded.
        resumable_chunk_size: The size of each chunk in bytes.
        resumable_total_size: The total size of the file.
        resumable_identifier: A unique identifier for the file upload.
        resumable_filename: The name of the file.
        resumable_relative_path: The relative path of the file.
        chunk_data: The raw byte content of the chunk.
    """
    params = {
        "target": target_path,
        "resumableChunkNumber": resumable_chunk_number,
        "resumableChunkSize": resumable_chunk_size,
        "resumableTotalSize": resumable_total_size,
        "resumableIdentifier": resumable_identifier,
        "resumableFilename": resumable_filename,
        "resumableRelativePath": resumable_relative_path,
    }
    return _make_request(context, "POST", "/v1/upload/resumable/", params=params, data=chunk_data)
