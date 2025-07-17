import requests
import pypdfium2 as pdfium
from mcp.server.fastmcp import Context
from typing import Dict, Any, Optional, List
from ._shared import _make_request, mcp, GENEPATTERN_URL


@mcp.tool()
def get_task_manifest(
    context: Context, task_name_or_lsid: str
) -> Dict[str, Any]:
    """
    Retrieves the manifest for a given task, returned in a Java properties file format.
    The manifest contains the core definitions and attributes of the task.

    Args:
        context: The MCP context.
        task_name_or_lsid: The name or Life Science Identifier (LSID) of the task.
    """
    return _make_request(
        context, "GET", f"/v1/tasks/{task_name_or_lsid}/manifest"
    )

# ------------------------------------------------------------------------------

@mcp.tool()
def get_all_tasks(
    context: Context, include_hidden: bool = False
) -> Dict[str, Any]:
    """
    Retrieves a JSON object containing the latest versions of all installed tasks (modules and pipelines)
    that are visible to the current user. Also includes lists of all categories and suites.

    Args:
        context: The MCP context.
        include_hidden: If True, tasks marked as hidden will be included in the response. Defaults to False.
    """
    params = {}
    if include_hidden:
        params["includeHidden"] = "true"
    return _make_request(context, "GET", "/v1/tasks/all.json", params=params)

# ------------------------------------------------------------------------------

@mcp.tool()
def get_task_details(
    context: Context,
    task_name_or_lsid: str,
    include_properties: bool = True,
    include_children: bool = True,
    include_eula: bool = True,
    include_support_files: bool = True,
    include_param_groups: bool = True,
    include_memory_settings: bool = True,
) -> Dict[str, Any]:
    """
    Retrieves a detailed JSON representation of a specific task by its name or LSID.
    Various flags can be used to control how much information is included.

    Args:
        context: The MCP context.
        task_name_or_lsid: The name or LSID of the task.
        include_properties: Whether to include metadata like author, privacy, quality, etc.
        include_children: For pipelines, whether to include details of the child tasks.
        include_eula: Whether to include information about End-User License Agreements.
        include_support_files: Whether to include a list of the task's support files.
        include_param_groups: Whether to include information about parameter groupings.
        include_memory_settings: Whether to include job memory settings from the manifest and server configuration.
    """
    params = {
        "includeProperties": include_properties,
        "includeChildren": include_children,
        "includeEula": include_eula,
        "includeSupportFiles": include_support_files,
        "includeParamGroups": include_param_groups,
        "includeMemorySettings": include_memory_settings,
    }
    return _make_request(
        context, "GET", f"/v1/tasks/{task_name_or_lsid}", params=params
    )

# ------------------------------------------------------------------------------

@mcp.tool()
def get_task_eula_info(
    context: Context,
    task_name_or_lsid: str,
    all: bool = False,
    pending: bool = True,
) -> Dict[str, Any]:
    """
    Gets the JSON representation of End-User License Agreements (EULAs) for a given module.
    The response is context-dependent, as 'pending' EULAs are those the current user has not yet accepted.

    Args:
        context: The MCP context.
        task_name_or_lsid: The name or LSID of the task.
        all: If True, include all EULAs associated with the task. Defaults to False.
        pending: If True, include EULAs that are pending acceptance by the user. Defaults to True.
                 The server default is to show pending EULAs if 'all' is not specified.
    """
    params = {}
    if all:
        params["all"] = "true"
    if pending:
        params["pending"] = "true"
    return _make_request(
        context, "GET", f"/v1/tasks/{task_name_or_lsid}/eulaInfo.json", params=params
    )

# ------------------------------------------------------------------------------

@mcp.tool()
def accept_task_eula(
    context: Context, task_name_or_lsid: str
) -> Dict[str, Any]:
    """
    Records the acceptance of a task's End-User License Agreement(s) for the current user.

    Args:
        context: The MCP context.
        task_name_or_lsid: The name or LSID of the task for which the EULA is being accepted.
    """
    return _make_request(
        context, "PUT", f"/v1/tasks/{task_name_or_lsid}/eulaAccept"
    )

# ------------------------------------------------------------------------------

@mcp.tool()
def get_task_code_example(
    context: Context, task_name_or_lsid: str, language: str
) -> Dict[str, Any]:
    """
    Generates and retrieves example code to run a specified task in a given programming language.

    Args:
        context: The MCP context.
        task_name_or_lsid: The name or LSID of the task.
        language: The programming language for the code example (e.g., 'Java', 'Python', 'R', 'REST', 'CommandLine').
    """
    params = {"language": language}
    return _make_request(
        context, "GET", f"/v1/tasks/{task_name_or_lsid}/code", params=params
    )

# ------------------------------------------------------------------------------

@mcp.tool()
def get_parameter_choice_info(
    context: Context, task_name_or_lsid: str, parameter_name: str
) -> Dict[str, Any]:
    """
    Retrieves the JSON representation of available choices for a task's input parameter.
    This is used for both static and dynamic drop-down menus in the user interface.

    Args:
        context: The MCP context.
        task_name_or_lsid: The name or LSID of the task.
        parameter_name: The name of the parameter for which to fetch choice information.
    """
    return _make_request(
        context, "GET", f"/v1/tasks/{task_name_or_lsid}/{parameter_name}/choiceInfo.json"
    )

# ------------------------------------------------------------------------------

def filter_tasks(context: Context, keyword: str, include_hidden: Optional[bool] = None) -> List[Any]:
    """Filter GenePattern tasks (modules) by keyword
    Args:
        context: The FastMCP context object.
        keyword: A string to filter modules by substring in name, description, tags, or lsid.
        include_hidden: If True, tasks marked as hidden will be included in the response. Defaults to False.
    Returns:
        A list of GenePattern tasks (modules) that match the keyword.
    """
    all_tasks = get_all_tasks(context, include_hidden)
    matches = list(filter(lambda x: keyword in x['name'] or
                                    ('description' in x and keyword in x['description']) or
                                    keyword in x['tags'] or
                                    keyword in x['lsid'], all_tasks['all_modules']))
    return matches

# ------------------------------------------------------------------------------

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
