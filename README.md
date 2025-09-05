# GenePattern MCP Server

A Model Context Protocol (MCP) server that lets AI coding assistants call GenePattern to list/run modules, manage jobs, and access data.

This README explains how to:
- Run the server (stdio and HTTP)
- Use Docker (image: genepattern/mcp)
- Connect from Claude Code, Cursor, or other MCP-enabled clients
- Configure all server arguments and environment variables


## Prerequisites
- Python 3.11+
- pip (or uv if preferred)
- A GenePattern API token (see “Get a GenePattern token” below)


## Installation
- With pip:
  - pip install -r requirements.txt
- With uv:
  - uv venv
  - source .venv/bin/activate
  - uv pip install -r requirements.txt


## Get a GenePattern token
You can authenticate with a Bearer token via the GENEPATTERN_KEY environment variable.

- If you already have an API token, set it:
  - export GENEPATTERN_KEY="YOUR_TOKEN"

- Or generate a token with the included helper:
  - python get-token.py -s https://cloud.genepattern.org/gp -u YOUR_USERNAME -p YOUR_PASSWORD
  - Follow the printed instructions to export GENEPATTERN_KEY

You can also switch to an HTTP header–based auth handler for HTTP mode; see the --auth-handler flag below.


## How to run the server
The server supports multiple transports via FastMCP.

- Stdio (recommended for local MCP clients):
  - python server.py --transport stdio

- HTTP (streamable-http, default):
  - python server.py --transport streamable-http --host 0.0.0.0 --port 3000

- SSE:
  - python server.py --transport sse --host 0.0.0.0 --port 3000

Environment variables can be used instead of flags; see the Arguments section.

Tip: Explore available MCP tools locally with:
- mcp dev server.py


## Docker
An official container is available at genepattern/mcp.

- Pull the image:
  - docker pull genepattern/mcp

- Run in HTTP mode (recommended for Docker):
  - docker run --rm \
      -e GENEPATTERN_URL=https://cloud.genepattern.org/gp \
      -e GENEPATTERN_KEY=YOUR_TOKEN \
      -e FASTMCP_TRANSPORT=streamable-http \
      -e FASTMCP_HOST=0.0.0.0 \
      -e FASTMCP_PORT=3000 \
      -p 3000:3000 \
      genepattern/mcp

- Using Authorization header instead of env token (HTTP only):
  - docker run --rm -p 3000:3000 \
      -e AUTH_HANDLER=genepattern_mcp._shared.HeaderAuthHandler \
      -e FASTMCP_TRANSPORT=streamable-http \
      genepattern/mcp
  Then send requests with: Authorization: Bearer YOUR_TOKEN

Note: Stdio transport is not practical from Docker containers; prefer HTTP when containerized.


## Connect from MCP-enabled clients
Below are examples. UI details may vary by client/version—consult your client’s documentation for the most current instructions.

### Claude Code (VS Code extension)
Use stdio transport when running the server locally.

- Open VS Code Settings (JSON) and add an entry like:
```json
{
  "mcpServers": {
    "genepattern": {
      "command": "python",
      "args": ["server.py", "--transport", "stdio"],
      "env": {
        "GENEPATTERN_URL": "https://cloud.genepattern.org/gp",
        "GENEPATTERN_KEY": "${env:GENEPATTERN_KEY}"
      }
    }
  }
}
```
- Or if running the MCP server independently:
```json
{
  "mcpServers": {
    "genepattern": {
      "type": "streamable-http",
      "url": "http://localhost:3000/mcp",
      "env": { 
        "GENEPATTERN_URL": "https://cloud.genepattern.org/gp",
        "GENEPATTERN_KEY": "<GP API TOKEN>"
      }
    }
  }
}
```
- Ensure GENEPATTERN_KEY is set in your shell environment (or inline in env above).

To connect to a Dockerized HTTP server instead (when supported by your client):
- Start the container as above, then configure the client to use the HTTP endpoint at http://localhost:3000 using the streamable-http transport (client support varies).

### Cursor
Cursor supports MCP servers as well.

- Add a new MCP server (via Cursor Settings UI) and point it to your local stdio command, e.g.:
{
  "mcpServers": {
    "genepattern": {
      "command": "python",
      "args": ["server.py", "--transport", "stdio"],
      "environment": {
        "GENEPATTERN_URL": "https://cloud.genepattern.org/gp",
        "GENEPATTERN_KEY": "YOUR_TOKEN"
      }
    }
  }
}
- Alternatively, for a Dockerized server, configure an HTTP connection to http://localhost:3000 if the client supports HTTP MCP.

### Other MCP-enabled software
- Stdio: invoke this repo’s server.py with --transport stdio.
- HTTP: connect to http://HOST:PORT using streamable-http or sse according to your client’s capabilities. If using Authorization header, set AUTH_HANDLER=genepattern_mcp._shared.HeaderAuthHandler and send Authorization: Bearer <token>.


## Arguments and environment variables
All flags correspond to environment variables; environment values are applied before CLI args.

- --genepattern, -g
  - Description: The URL of the GenePattern server, including /gp
  - Env: GENEPATTERN_URL
  - Default: https://cloud.genepattern.org/gp

- --key, -k
  - Description: Your GenePattern API key (Bearer token)
  - Env: GENEPATTERN_KEY
  - Default: None

- --auth-handler, -a
  - Description: Full Python path to an AuthHandler class to retrieve the API key. Built-ins:
    - genepattern_mcp._shared.EnvAuthHandler (default, reads GENEPATTERN_KEY)
    - genepattern_mcp._shared.HeaderAuthHandler (reads Authorization: Bearer <token> for HTTP)
  - Env: AUTH_HANDLER
  - Default: genepattern_mcp._shared.EnvAuthHandler

- --transport, -t
  - Description: Transport protocol to use (streamable-http, stdio, or sse)
  - Env: FASTMCP_TRANSPORT
  - Default: streamable-http

- --port, -p
  - Description: Port to run the MCP server on (HTTP/SSE only)
  - Env: FASTMCP_PORT
  - Default: 3000

- --host, -H
  - Description: Host/interface to bind (HTTP/SSE only)
  - Env: FASTMCP_HOST
  - Default: 0.0.0.0


## Security notes
- Treat GENEPATTERN_KEY like a password. Prefer environment variables over hardcoding.
- If exposing HTTP to a network, ensure you control access and consider a reverse proxy/TLS.


## Development
- List and test tools locally:
  - mcp dev server.py


## License
See LICENSE.
