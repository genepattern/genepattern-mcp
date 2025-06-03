# server.py
import requests
import json
from mcp.server.fastmcp import FastMCP
import httpx
import asyncio
import os

# Run on port 3000, if not specified - avoids conflicts with Django
if "FASTMCP_PORT" not in os.environ: os.environ["FASTMCP_PORT"] = "3000"

# Create an MCP server
mcp = FastMCP("Demo")

# use beta because cloud does not yet allow anonymous retrieval of module docs
GP_HOST = "https://beta.genepattern.org/"
GP_URL = GP_HOST +"gp/"
GP_API_BASE = GP_URL +"/rest/v1/" # tasks/all.json"

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b



# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


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
async def get_module_documentation(module_name_or_lsid: str) -> bytes | None:
    """
    Fetch and save the documentation for a GenePattern module.

    Args:
        module_name_or_lsid: The name or LSID of the module. TBD is the LSID lookup

    Returns:
        The file contents of the documentation as bytes, or None if the module or documentation is not found.
    """

    module_json = await get_all_modules_list()
    module_dictionary = {module["name"]: module for module in module_json}


    # Find the module by name or LSID
    module = module_dictionary.get(module_name_or_lsid)
    if not module:
        return None

    # Get the documentation URL
    documentation_url = module.get("documentation")
    if not documentation_url:
        print(f"No documentation found for module {module_name_or_lsid}")
        return None

    # Ensure the cache directory exists
    cache_dir = "module_doc_cache"
    os.makedirs(cache_dir, exist_ok=True)

    # Use the LSID as the unique filename
    lsid = module["lsid"]
    file_path = os.path.join(cache_dir, lsid)

    # Fetch the documentation
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            print(f"Fetching documentation for {module_name_or_lsid} from {  GP_HOST + documentation_url}")
            response = await client.get(GP_HOST + documentation_url, timeout=30.0)
            response.raise_for_status()
            file_contents = response.content

            # Save the file
            with open(file_path, "wb") as file:
                file.write(file_contents)

            return file_contents
        except Exception:
            return None




def main():
    # Call the async function using asyncio.run
    result = asyncio.run(all_categories())
    print(result)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="streamable-http")


