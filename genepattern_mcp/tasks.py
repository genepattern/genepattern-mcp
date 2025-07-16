from mcp.server.fastmcp import Context
from typing import Dict, Any, Optional, List
from ._shared import _make_request, mcp, GENEPATTERN_URL


@mcp.tool()
def get_all_tasks(context: Context, include_hidden: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves a list of all available tasks (modules)."""
    params = {"includeHidden": include_hidden}
    return _make_request(context, "GET", "/v1/tasks/all.json", params=params)


def filter_tasks(context: Context, keyword: str, include_hidden: Optional[str] = None) -> List[Any]:
    """Filter GenePattern tasks (modules) by keyword
    Args:
        keyword: A string to filter modules by substring in name, description, tags, or lsid.
    Returns:
        A list of GenePattern tasks (modules) that match the keyword.
    """
    all_tasks = get_all_tasks(context, include_hidden)
    matches = list(filter(lambda x: keyword in x['name'] or
                                    ('description' in x and keyword in x['description']) or
                                    keyword in x['tags'] or
                                    keyword in x['lsid'], all_tasks['all_modules']))
    return matches


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


import os
import requests
import pypdfium2 as pdfium
from typing import Optional, Dict, Any

# This code assumes the existence of the previously defined tools and placeholders
# (e.g., @tool, Context, get_all_tasks)

# The base host for constructing full documentation URLs


@mcp.tool()
def get_task_documentation(context: Context, task_name_or_lsid: str) -> Optional[str]:
    """
    Fetches the documentation for a GenePattern task (module) and returns it as a string.
    Converts PDF documentation to text if necessary.

    Args:
        context: The FastMCP context object.
        task_name_or_lsid: The name or LSID of the module.

    Returns:
        The documentation content as a string, or None if not found or conversion fails.
    """
    # 1. Fetch the list of all available modules using the existing tool
    all_tasks_response = get_all_tasks(context)

    # The API returns a dictionary with an 'all_modules' key containing the list
    if not all_tasks_response or 'all_modules' not in all_tasks_response:
        print("Error: Could not retrieve the list of modules from the server.")
        return None

    module_list = all_tasks_response['all_modules']

    # 2. Find the target module by its name or LSID
    target_module = None
    for module in module_list:
        if module.get('name') == task_name_or_lsid or module.get('lsid') == task_name_or_lsid:
            target_module = module
            break

    if not target_module:
        print(f"Error: Module '{task_name_or_lsid}' could not be found.")
        return None

    # 3. Get the documentation URL and determine its MIME type
    doc_url = target_module.get("documentation")
    doc_mimetype = target_module.get("documentation_mimetype")

    if not doc_url:
        print(f"Warning: No documentation URL is available for module '{task_name_or_lsid}'.")
        return None

    # Infer MIME type if it's not explicitly provided
    if not doc_mimetype:
        doc_mimetype = 'application/pdf' if doc_url.lower().endswith('.pdf') else 'text/html'
        print(f"Warning: MIME type not specified. Inferred as '{doc_mimetype}'.")

    # 4. Fetch the documentation content from its URL
    try:
        full_url = f"{GENEPATTERN_URL[:-3]}{doc_url}"
        print(f"Fetching documentation for '{task_name_or_lsid}' from {full_url}...")

        # Documentation is typically public, so no authorization header is needed here.
        response = requests.get(full_url, timeout=30, allow_redirects=True)
        response.raise_for_status()
        doc_bytes = response.content

    except requests.exceptions.RequestException as e:
        print(f"Error: Network request to fetch documentation failed: {e}")
        return None

    # 5. Process the downloaded content based on its type
    print(f"Processing content with MIME type: {doc_mimetype}...")
    if "pdf" in doc_mimetype:
        try:
            # Use pypdfium2 to extract text directly from the PDF bytes
            pdf_doc = pdfium.PdfDocument(doc_bytes)
            text_content = "\n".join(page.get_textpage().get_text_range() for page in pdf_doc)
            return text_content
        except Exception as e:
            print(f"Error: Failed to convert PDF documentation to text: {e}")
            return None
    elif "text" in doc_mimetype or "html" in doc_mimetype:
        try:
            # Decode the text content, with a fallback for encoding issues
            return doc_bytes.decode('utf-8')
        except UnicodeDecodeError:
            print("Warning: UTF-8 decoding failed. Falling back to latin-1.")
            return doc_bytes.decode('latin-1')
    else:
        print(f"Error: Unsupported documentation MIME type '{doc_mimetype}'.")
        return None