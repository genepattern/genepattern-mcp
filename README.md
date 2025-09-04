# genepattern-mcp

# Installation

> pip install -r requirements.txt

If using uv, you might need to do it like this instead

> uv venv
> source .venv/bin/activate
> uv pip install -r requirements.txt


# Dev server testing

> mcp dev server.py

# Connect to GenePattern MCP

```json
{
  "mcpServers": {
    "genepattern": {
      "type": "streamable-http",
      "url": "http://localhost:3000/mcp",
      "env": { "GENEPATTERN_KEY": "<GP API TOKEN>" }
    }
  }
}
```
