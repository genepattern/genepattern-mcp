# server.py
import requests
import json
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Demo")


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


@mcp.resource("data://all_modules", mime_type="application/json")
def all_modules() -> str:
    """Filter GenePattern modules for those matching a particular keyword"""
    response = requests.get('https://cloud.genepattern.org/gp/rest/v1/tasks/all.json')
    response.raise_for_status()
    parsed = response.json()
    return json.dumps(parsed['all_modules'])


@mcp.resource("data://filter_modules/{keyword}", mime_type="application/json")
def filter_modules(keyword: str = '') -> str:
    """Filter GenePattern modules for those matching a particular keyword"""
    response = requests.get('https://cloud.genepattern.org/gp/rest/v1/tasks/all.json')
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
    response = requests.get('https://cloud.genepattern.org/gp/rest/v1/tasks/all.json')
    response.raise_for_status()
    parsed = response.json()
    modules_names = list(map(lambda x: x['name'], parsed['all_modules']))
    return json.dumps(modules_names)


@mcp.resource("data://all_categories", mime_type="application/json")
def all_categories() -> str:
    """Get the names of all GenePattern module categories"""
    response = requests.get('https://cloud.genepattern.org/gp/rest/v1/tasks/all.json')
    response.raise_for_status()
    parsed = response.json()
    category_names = list(map(lambda x: x['name'], parsed['all_categories']))
    return json.dumps(category_names)


def main():
    # Call the async function using asyncio.run
    result = asyncio.run(get_all_modules_list())
    print(result)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
    #main()


