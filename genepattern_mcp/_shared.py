import abc
import importlib
import os
import requests
from mcp.server import FastMCP
from mcp.server.fastmcp import Context
from typing import Optional, Dict, Any


# Create the FastMCP server instance
mcp = FastMCP("GenePattern")

# Set the base URL for the GenePattern RESTful API
GENEPATTERN_URL = os.environ.get("GENEPATTERN_URL", "https://cloud.genepattern.org/gp")
REST_URL = f"{GENEPATTERN_URL}/rest"


class AuthHandler(abc.ABC):
    """Abstract base class for authentication handlers.
    Subclasses must implement the `get_api_key` method.
    """
    @abc.abstractmethod
    def get_api_key(self, context: Context) -> Optional[str]:
        """Retrieves the GenePattern API key."""
        raise NotImplementedError


class EnvAuthHandler(AuthHandler):
    """
    Default authentication handler that retrieves the API key
    from the GENEPATTERN_KEY environment variable.
    """
    def get_api_key(self, context: Context) -> Optional[str]:
        """Retrieves the API key from the environment."""
        return os.environ.get("GENEPATTERN_KEY")


# The active auth handler instance, initialized to the default
_auth_handler: AuthHandler = EnvAuthHandler()


def set_auth_handler(class_path: str):
    """
    Dynamically imports and instantiates the specified AuthHandler class.
    Args:
        class_path: The full Python path to the handler class (e.g., 'my_module.MyClass').
    Raises:
        ImportError: If the class or module cannot be found.
        TypeError: If the specified class is not a subclass of AuthHandler.
    """
    global _auth_handler
    try:
        module_path, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        handler_class = getattr(module, class_name)
        if not issubclass(handler_class, AuthHandler):
            raise TypeError(f"Class '{class_path}' must be a subclass of 'AuthHandler'")
        _auth_handler = handler_class()
    except (ImportError, AttributeError, ValueError) as e:
        raise ImportError(f"Could not import or instantiate AuthHandler from '{class_path}': {e}") from e


def _make_request(context: Context, method: str, path: str, params: Optional[Dict[str, Any]] = None,
                  json_data: Optional[Dict[str, Any]] = None, data: Optional[Any] = None,
                  files: Optional[Dict[str, Any]] = None, extra_headers: Optional[Dict[str, str]] = None) -> Any:
    """
    Helper function to make authenticated requests to the GenePattern API.

    Args:
        context: The FastMCP context object.
        method: The HTTP method (e.g., 'GET', 'POST').
        path: The API endpoint path.
        params: URL query parameters.
        json_data: JSON payload for the request body.
        data: Raw data for the request body.
        files: Files for multipart/form-data uploads.
        extra_headers: Any additional headers to include.

    Returns:
        The API response, typically a dictionary from JSON or text.

    Raises:
        Exception: If the API request fails.
    """
    api_key = _auth_handler.get_api_key(context)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }
    if extra_headers: headers.update(extra_headers)

    # Filter out None values from params so they aren't sent
    if params: params = {k: v for k, v in params.items() if v is not None}

    try:
        response = requests.request(
            method=method,
            url=f"{REST_URL}{path}",
            headers=headers,
            params=params,
            json=json_data,
            data=data,
            files=files
        )
        response.raise_for_status()

        if response.status_code == 204:  # No Content
            return {"status": "success", "message": "Request completed with no content."}

        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type: return response.json()
        if "text/" in content_type: return response.text

        return response.content

    except requests.exceptions.HTTPError as http_err:
        error_message = f"HTTP Error: {http_err.response.status_code} for URL: {http_err.request.url}\nResponse: {http_err.response.text}"
        raise Exception(error_message) from http_err
    except requests.exceptions.RequestException as req_err:
        raise Exception(f"Request Exception: {req_err}") from req_err
