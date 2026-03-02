import abc
import importlib
import os
import requests
import base64
from mcp.server import FastMCP
from mcp.server.fastmcp import Context
from typing import Optional, Dict, Any
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


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
        """Retrieves the API key from the environment"""
        return os.environ.get("GENEPATTERN_KEY")


class HeaderAuthHandler(AuthHandler):
    """
    Default authentication handler that retrieves the API key
    from the Authorization header in the request
    """
    def get_api_key(self, context: Context) -> Optional[str]:
        """Retrieves the API key from the request's Authorization header"""
        scope = context.request_context.request.scope
        token = scope.get("token")
        return token


class GenePatternMCP(FastMCP):
    """A custom FastMCP server for GenePattern, extending the base FastMCP class."""
    auth_handler: AuthHandler

    def __init__(self, name: str, auth_handler: Optional[AuthHandler] = None):
        super().__init__(name)
        self.auth_handler = auth_handler or EnvAuthHandler()
        
        # Set system prompt with instructions for optimal tool usage
        self.system_prompt = """You are an AI assistant that helps users interact with GenePattern for genomics analysis.

IMPORTANT: When users ask about output files from their jobs, follow this two-step pattern:
1. First, call get_recent_jobs(include_output_files=False) to get a lightweight list of recent jobs and identify the job ID
2. Then, call get_job_details(job_id, include_output_files=True) to retrieve the output files for just that specific job

This pattern is critical because:
- Including output files for ALL recent jobs in a single call can exceed token limits and cause failures
- The two-step approach is much more efficient and provides better results
- Always start with get_recent_jobs(include_output_files=False) - NEVER set include_output_files=True in get_recent_jobs

For any other job queries that don't require output file details, use get_recent_jobs with its default parameters.
"""

    class AuthHandlerMiddleware(BaseHTTPMiddleware):
        """ Middleware to handle authentication by extracting the bearer token"""

        async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
            """ Handles the request to extract the bearer token from the Authorization header."""
            request.scope["token"] = None                        # Initialize the token in the scope to None
            auth_header = request.headers.get("Authorization")  # Check for the Authorization header
            if auth_header:                                     # Should be in the format "Bearer <token>"
                parts = auth_header.split()                     # Check if the header has two parts
                if len(parts) == 2 and parts[0].lower() == "bearer":  # and the first part is "Bearer"
                    token = parts[1]
                    request.scope["token"] = token              # Add the token to the request's scope
            response = await call_next(request)                 # Proceed to the next middleware
            return response

    async def run_streamable_http_async(self) -> None:
        """Overrides the default run_streamable_http_async method to add the middleware."""
        import uvicorn

        starlette_app = self.streamable_http_app()
        starlette_app.add_middleware(self.AuthHandlerMiddleware) # Add AuthHandler middleware

        config = uvicorn.Config(
            starlette_app,
            host=self.settings.host,
            port=self.settings.port,
            log_level=self.settings.log_level.lower(),
        )
        server = uvicorn.Server(config)
        await server.serve()

    def set_auth_handler(self, class_path: str):
        """
        Dynamically imports and instantiates the specified AuthHandler class.
        Args:
            class_path: The full Python path to the handler class (e.g., 'my_module.MyClass').
        Raises:
            ImportError: If the class or module cannot be found.
            TypeError: If the specified class is not a subclass of AuthHandler.
        """
        try:
            module_path, class_name = class_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            handler_class = getattr(module, class_name)
            if not issubclass(handler_class, AuthHandler):
                raise TypeError(f"Class '{class_path}' must be a subclass of 'AuthHandler'")
            self.auth_handler = handler_class()
        except (ImportError, AttributeError, ValueError) as e:
            raise ImportError(f"Could not import or instantiate AuthHandler from '{class_path}': {e}") from e


# Create the FastMCP server instance
mcp = GenePatternMCP("GenePattern")

# Set the base URL for the GenePattern RESTful API
GENEPATTERN_URL = os.environ.get("GENEPATTERN_URL", "https://cloud.genepattern.org/gp")
REST_URL = f"{GENEPATTERN_URL}/rest"

# Configuration for local file operations
LOCAL_FILES_ENABLED = os.environ.get("LOCAL_FILES_ENABLED", "True").lower() in ("true", "1", "yes")


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
    api_key = mcp.auth_handler.get_api_key(context)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "*/*",  # Accept any content type to avoid 406 errors
    }
    if extra_headers: headers.update(extra_headers)

    # Filter out None values from params so they aren't sent
    if params: params = {k: v for k, v in params.items() if v is not None}

    print(f"Making {method} request to {REST_URL}{path} with params={params}, json_data={json_data}, data={'<binary>' if data else None}, files={'<files>' if files else None}, headers={headers}")

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

        print(response.url)
        print(response.headers)
        print(response.content)

        if response.status_code == 204:  # No Content
            return {"status": "success", "message": "Request completed with no content."}

        # Extract content type without parameters (e.g., "text/html; charset=utf-8" -> "text/html")
        content_type = response.headers.get("Content-Type", "").split(';')[0].strip()

        # Handle JSON responses directly (keep backward compatibility)
        if "application/json" in content_type:
            return response.json()

        # Handle text-based responses (HTML, plain text, etc.)
        if content_type.startswith("text/"):
            return {content_type: response.text}

        # Handle binary content - base64 encode it
        if content_type:
            encoded_content = base64.b64encode(response.content).decode('utf-8')
            return {content_type: encoded_content}

        # Fallback for unknown content type - treat as binary
        encoded_content = base64.b64encode(response.content).decode('utf-8')
        return {"application/octet-stream": encoded_content}

    except requests.exceptions.HTTPError as http_err:
        error_message = f"HTTP Error: {http_err.response.status_code} for URL: {http_err.request.url}\nResponse: {http_err.response.text}"
        raise Exception(error_message) from http_err
    except requests.exceptions.RequestException as req_err:
        raise Exception(f"Request Exception: {req_err}") from req_err
