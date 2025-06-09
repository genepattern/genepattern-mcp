# server.py
import requests
import json
from mcp.server.fastmcp import FastMCP
import httpx
import asyncio
import os
from typing import Optional
import pypdfium2 as pdfium

# Run on port 3000, if not specified - avoids conflicts with Django
if "FASTMCP_PORT" not in os.environ: os.environ["FASTMCP_PORT"] = "3000"

# Create an MCP server
mcp = FastMCP("Demo")

# use beta because cloud does not yet allow anonymous retrieval of module docs
GP_HOST = "https://beta.genepattern.org/"
GP_URL = GP_HOST +"gp/"
GP_API_BASE = GP_URL +"/rest/v1/" # tasks/all.json"


async def get_all_modules_list():
    """
    Fetch a list of all installed GenePattern modules from the GenePattern cloud server.

    Returns:
        A dictionary keyed by module name, containing each module's details if the request
        is successful, or None if the request fails or encounters an error.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(GP_API_BASE + "tasks/all.json", timeout=30.0)
            response.raise_for_status()
            data = response.json()
            return data["all_modules"]
        except Exception as e:
            print(f"Error fetching modules: {e}")
            return None


@mcp.resource("data://all_modules", mime_type="application/json")
async def all_modules() -> str:
    """All GenePattern modules available on the GenePattern server"""

    return json.dumps(await get_all_modules_list())


@mcp.resource("data://filter_modules/{keyword}", mime_type="application/json")
def filter_modules(keyword: str = '') -> str:
    """Filter GenePattern modules for those matching a particular keyword"""
    response = requests.get(GP_API_BASE+'tasks/all.json')
    response.raise_for_status()
    parsed = response.json()
    matches = list(filter(lambda x: keyword in x['name'] or
                                    ('description' in x and keyword in x['description']) or
                                    keyword in x['tags'] or
                                    keyword in x['lsid'], parsed['all_modules']))
    return json.dumps(matches)


@mcp.resource("data://module_names", mime_type="application/json")
def module_names() -> str:
    """Get the names of all available GenePattern modules"""
    response = requests.get(GP_API_BASE+'tasks/all.json')
    response.raise_for_status()
    parsed = response.json()
    modules_names = list(map(lambda x: x['name'], parsed['all_modules']))
    return json.dumps(modules_names)


@mcp.resource("data://all_categories", mime_type="application/json")
def all_categories() -> str:
    """Get the names of all GenePattern module categories"""
    response = requests.get(GP_API_BASE+'tasks/all.json')
    response.raise_for_status()
    parsed = response.json()
    category_names = list(map(lambda x: x['name'], parsed['all_categories']))
    return json.dumps(category_names)


@mcp.tool()
async def get_module_documentation(module_name_or_lsid: str) -> Optional[str]:
    """
    Fetch and save the documentation for a GenePattern module, returning it as a Unicode string.
    Converts PDF documentation to text.

    Args:
        module_name_or_lsid: The name or LSID of the module.

    Returns:
        The file contents of the documentation as a Unicode string, or None if the module,
        documentation is not found, or conversion fails.
    """

    module_json = await get_all_modules_list()
    module_dictionary = {module["name"]: module for module in module_json}

    # Find the module by name or LSID
    module = module_dictionary.get(module_name_or_lsid)
    if not module:
        return None

    # Get the documentation URL and mimetype
    documentation_url = module.get("documentation")
    documentation_mimetype = module.get("documentation_mimetype")  # Assuming this is now available

    if not documentation_url or not documentation_mimetype:
        print(f"No documentation URL or mimetype found for module {module_name_or_lsid}")
        return None

    # Ensure the cache directory exists
    cache_dir = "module_doc_cache"
    os.makedirs(cache_dir, exist_ok=True)

    # Use the LSID as the unique filename
    lsid = module["lsid"]
    file_path = os.path.join(cache_dir, lsid)

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            full_url = GP_HOST + documentation_url
            print(f"Fetching documentation for {module_name_or_lsid} from {full_url}")
            response = await client.get(full_url, timeout=30.0)
            response.raise_for_status()
            file_contents_bytes = response.content

            # Save the file (optional, but good for caching)
            with open(file_path, "wb") as file:
                file.write(file_contents_bytes)

            # Determine content type and return appropriate string
            if "text/" in documentation_mimetype:
                try:
                    return file_contents_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    print(
                        f"Warning: Could not decode text content for {module_name_or_lsid} with utf-8. Trying latin-1.")
                    return file_contents_bytes.decode('latin-1')  # Fallback for common text encodings
            elif documentation_mimetype == "application/pdf":
                try:
                    # Save PDF to a temporary file to allow pypdfium2 to read it
                    temp_pdf_path = f"{file_path}.pdf"
                    with open(temp_pdf_path, "wb") as temp_pdf_file:
                        temp_pdf_file.write(file_contents_bytes)

                    # Convert PDF to text using pypdfium2
                    doc = pdfium.PdfDocument(temp_pdf_path)
                    text_content = ""
                    for i in range(len(doc)):
                        page = doc[i]
                        text_content += page.get_text_page().get_text_range() + "\n"
                    doc.close()
                    os.remove(temp_pdf_path)  # Clean up temporary PDF file
                    return text_content
                except Exception as e:
                    print(f"Error converting PDF for {module_name_or_lsid}: {e}")
                    return None
            else:
                print(f"Unsupported MIME type for {module_name_or_lsid}: {documentation_mimetype}")
                return None

        except httpx.RequestError as e:
            print(f"HTTP request failed for {module_name_or_lsid}: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"HTTP status error for {module_name_or_lsid}: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred for {module_name_or_lsid}: {e}")
            return None




def main():
    # Call the async function using asyncio.run
    result = asyncio.run(all_categories())
    print(result)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="streamable-http")


