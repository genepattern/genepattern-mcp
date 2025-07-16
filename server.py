#!/usr/bin/env python3

import argparse
import os

#############################################################################
# This script sets up a GenePattern MCP server.
# It allows users to interact with GenePattern modules, jobs and files.
#
# To run the server, you can use the following command:
# > python server.py --genepattern https://cloud.genepattern.org/gp \
#         --key YOUR_API_KEY --transport streamable-http --port 3000
#
# To explore the available tools, you can use:
# > mcp dev server.py
#############################################################################

# Handle any command line arguments and/or environment variables
parser = argparse.ArgumentParser(description="Configure GenePattern MCP Server",
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--genepattern', '-g',
    type=str, default=os.getenv('GENEPATTERN_URL', 'https://cloud.genepattern.org/gp'),
    help=(
        "The URL of the GenePattern server, including /gp.\n"
        "Env Variable: GENEPATTERN_URL\n"
        "Default: https://cloud.genepattern.org/gp"
    )
)

parser.add_argument('--key', '-k',
    type=str, default=os.getenv('GENEPATTERN_KEY'), # Default is None if not set
    help=(
        "Your GenePattern API key.\n"
        "Env Variable: GENEPATTERN_KEY\n"
        "Default: None"
    )
)
parser.add_argument('--auth-handler', '-a',
    type=str, default=os.getenv('AUTH_HANDLER', 'genepattern_mcp._shared.EnvAuthHandler'),
    help=(
        "The full Python path to the AuthHandler class to use for API key management.\n"
        "Example: genepattern_mcp.custom.DatabaseAuthHandler\n"
        "Env Variable: AUTH_HANDLER\n"
        "Default: genepattern_mcp._shared.EnvAuthHandler"
    )
)
parser.add_argument('--transport', '-t',
    type=str, default=os.getenv('FASTMCP_TRANSPORT', 'streamable-http'),
    help=(
        "Transport protocol to use (streamable-http, stdio or sse) \n"
        "Env Variable: FASTMCP_TRANSPORT\n"
        "Default: streamable-http"
    )
)
parser.add_argument('--port', '-p',
    type=int, default=os.getenv('FASTMCP_PORT', 3000),
    help=(
        "The port on which to run the MCP server.\n"
        "Env Variable: FASTMCP_PORT\n"
        "Default: 3000"
    )
)
args, unknown = parser.parse_known_args()

# Set up the MCP server and AuthHandler (Imported here to as to respect environment variables)
os.environ["GENEPATTERN_URL"] = str(args.genepattern)
if args.key: os.environ["GENEPATTERN_KEY"] = str(args.key)
os.environ["FASTMCP_PORT"] = str(args.port)
from genepattern_mcp._shared import mcp, set_auth_handler
try: set_auth_handler(args.auth_handler)
except (ImportError, TypeError) as e:
    print(f"Error: Could not set authentication handler. {e}")
    exit(1)

# Import all tools (imported here because they depend on the mcp instance)
from genepattern_mcp.files import *
from genepattern_mcp.jobs import *
from genepattern_mcp.system import *
from genepattern_mcp.tasks import *
from genepattern_mcp.uploads import *

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport=args.transport)
