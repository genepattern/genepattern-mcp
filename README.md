<!-- Banner -->
<p align="center">
  <!-- Replace with your actual banner image -->
  <img src="https://raw.githubusercontent.com/genepattern/genepattern-mcp/main/docs/banner.png" alt="GenePattern MCP Banner" width="800"/>
</p>

<h1 align="center">GenePattern MCP Server</h1>

<div align="center">
  <em>Bridge any AI coding assistant directly to GenePattern — run bioinformatics modules, manage cloud jobs, and stream results, all through natural language.</em>

[![Python](https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: BSD-3](https://img.shields.io/badge/license-BSD--3--Clause-green)](LICENSE)
[![Powered by GenePattern](https://img.shields.io/badge/Powered%20by-GenePattern-blueviolet)](https://genepattern.ucsd.edu/)

</div>

---

## Why GenePattern MCP?

Modern AI assistants are extraordinarily good at reasoning — but they can't run a gene expression pipeline or execute bioinformatics on their own. We built GenePattern MCP to close that gap.

By implementing the [Model Context Protocol (MCP)](https://modelcontextprotocol.io), this server exposes the full GenePattern REST API as a set of structured, type-safe tools that any MCP-compatible AI client (Claude, Cursor, GitHub Copilot, and more) can call directly. The result: your AI assistant can now:

- 🧬 **Search, inspect, and execute** hundreds of peer-reviewed genomic analysis modules
- 🤖 **Chain bioinformatic tasks** into multi-step AI-driven workflows — no manual API calls required
- ☁️ **Scale effortlessly** on GenePattern's cloud infrastructure at [cloud.genepattern.org](https://cloud.genepattern.org)
- 📊 **Guarantee reproducibility** — every job is tracked by LSID and stored with full provenance

> From raw expression data to publication-ready insights — powered by a conversation.

---

## Feature Highlights

| Feature | Description |
|---|---|
| 🧬 **Genomic Integration** | Access 200+ curated modules: differential expression, pathway analysis, single-cell, proteomics, and more |
| 🤖 **AI/ML Workflows** | Let your LLM orchestrate multi-step pipelines end-to-end via natural language prompts |
| ☁️ **Cloud Scalability** | Jobs run on GenePattern's managed cloud — no local compute needed |
| 📊 **Reproducible Science** | Every module is versioned by LSID; every job is logged and retrievable |
| 🔌 **Multi-Transport** | `stdio` for local clients, `streamable-http` / `SSE` for remote or containerized deployments |
| 🔐 **Flexible Auth** | Pluggable `AuthHandler` system — env-var token, HTTP Bearer header, or bring your own |
| 🐳 **Docker-Ready** | Official image at `genepattern/mcp`; zero-config cloud deployment |

---

## Prerequisites

- **Python 3.11+**
- A **GenePattern API token** (see [Get a Token](#get-a-genepattern-token) below)
- `pip` or `uv`

---

## Installation

**With pip:**
```bash
pip install -r requirements.txt
```

**With uv:**
```bash
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
```

---

## Get a GenePattern Token

You need a Bearer token to authenticate with GenePattern.

**Option A — You already have a token:**
```bash
export GENEPATTERN_KEY="YOUR_TOKEN"
```

**Option B — Generate one with the included helper:**
```bash
python get-token.py -s https://cloud.genepattern.org/gp \
                    -u YOUR_USERNAME \
                    -p YOUR_PASSWORD
# Follow the printed instructions to export GENEPATTERN_KEY
```

---

## Quick Start

### 1. Start the server (local stdio — recommended for AI clients)
```bash
export GENEPATTERN_KEY="YOUR_TOKEN"
python server.py --transport stdio
```

### 2. Run a bioinformatic analysis via your AI assistant

Once connected, ask your AI assistant something like:

> *"Run PreprocessDataset on `all_aml_test.gct`, threshold at 20/1500, and download the result."*

The MCP server will:
1. Look up the `PreprocessDataset` module LSID automatically
2. Submit the job to GenePattern cloud
3. Poll for completion and return the output file paths

### 3. Explore available tools interactively
```bash
mcp dev server.py
```

---

## Running the Server

The server supports three transport modes via [FastMCP](https://github.com/jlowin/fastmcp).

| Mode | Command |
|---|---|
| **stdio** (local AI clients) | `python server.py --transport stdio` |
| **HTTP** (remote / Docker) | `python server.py --transport streamable-http --host 0.0.0.0 --port 3000` |
| **SSE** | `python server.py --transport sse --host 0.0.0.0 --port 3000` |

> **Testing with GenePattern Copilot:**
> ```bash
> python server.py --transport streamable-http --host 0.0.0.0 --port 3000 \
>     --auth-handler genepattern_mcp._shared.HeaderAuthHandler
> ```

---

## Docker

Pull and run the official image in seconds:

```bash
docker pull genepattern/mcp
```

**Run in HTTP mode:**
```bash
docker run --rm \
  -e GENEPATTERN_URL=https://cloud.genepattern.org/gp \
  -e GENEPATTERN_KEY=YOUR_TOKEN \
  -e FASTMCP_TRANSPORT=streamable-http \
  -e FASTMCP_HOST=0.0.0.0 \
  -e FASTMCP_PORT=3000 \
  -p 3000:3000 \
  genepattern/mcp
```

**Using Authorization header instead of an env token (stateless, multi-user HTTP):**
```bash
docker run --rm -p 3000:3000 \
  -e AUTH_HANDLER=genepattern_mcp._shared.HeaderAuthHandler \
  -e FASTMCP_TRANSPORT=streamable-http \
  genepattern/mcp
# Clients send: Authorization: Bearer YOUR_TOKEN
```

> **Note:** `stdio` transport is impractical inside Docker containers. Use `streamable-http` when containerized.

---

## Connect from MCP-Enabled Clients

### Claude Code (VS Code)

**Local stdio (recommended):**
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

**Remote HTTP server:**
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

### Cursor

Add via **Cursor Settings → MCP Servers**:
```json
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
```

### Other MCP Clients
- **stdio:** invoke `server.py --transport stdio`
- **HTTP/SSE:** connect to `http://HOST:PORT` using the appropriate transport
- **Multi-user HTTP:** set `AUTH_HANDLER=genepattern_mcp._shared.HeaderAuthHandler` and pass `Authorization: Bearer <token>` per request

---

## Configuration Reference

All CLI flags have a corresponding environment variable. Environment variables are applied before CLI arguments.

| Flag | Env Variable | Default | Description |
|---|---|---|---|
| `--genepattern`, `-g` | `GENEPATTERN_URL` | `https://cloud.genepattern.org/gp` | GenePattern server URL (include `/gp`) |
| `--key`, `-k` | `GENEPATTERN_KEY` | `None` | Your GenePattern API Bearer token |
| `--auth-handler`, `-a` | `AUTH_HANDLER` | `EnvAuthHandler` | Full Python path to an `AuthHandler` class (see below) |
| `--transport`, `-t` | `FASTMCP_TRANSPORT` | `streamable-http` | Transport protocol: `streamable-http`, `stdio`, or `sse` |
| `--port`, `-p` | `FASTMCP_PORT` | `3000` | Port to listen on (HTTP/SSE only) |
| `--host`, `-H` | `FASTMCP_HOST` | `0.0.0.0` | Host interface to bind (HTTP/SSE only) |
| `--local-files`, `-l` | `LOCAL_FILES_ENABLED` | `True` | Enable local file upload/download tools |

### Auth Handlers

| Class | Behavior |
|---|---|
| `genepattern_mcp._shared.EnvAuthHandler` | *(default)* Reads `GENEPATTERN_KEY` from environment |
| `genepattern_mcp._shared.HeaderAuthHandler` | Reads `Authorization: Bearer <token>` from each HTTP request |
| *custom* | Subclass `AuthHandler` and implement `get_api_key(context)` |

### Local File Tools

When `--local-files` is `False`, the following tools are **disabled**:

- `upload_whole_file`
- `download_job_results`
- `upload_file`
- `upload_job_input_from_body`
- `upload_job_input_from_form`
- `upload_job_output`

---

## Security Notes

- Treat `GENEPATTERN_KEY` like a password — prefer environment variables over hardcoding tokens.
- When exposing the HTTP server to a network, put it behind a reverse proxy with TLS (e.g., nginx + Let's Encrypt).
- For multi-user deployments, use `HeaderAuthHandler` so each user supplies their own token per request.

---

## Contributing & Community

We believe the best bioinformatics tools are built by the community, for the community. All skill levels welcome — whether you're a genomics researcher, an ML engineer, or just someone who wants to ask an AI to run a pathway analysis.

**Ways to get involved:**

- 🐛 **Found a bug?** [Open an issue](https://github.com/genepattern/genepattern-mcp/issues) — we triage actively.
- 💡 **Have a feature idea?** Start a [Discussion](https://github.com/genepattern/genepattern-mcp/discussions) — we love hearing about new use cases.
- 🔧 **Want to contribute code?** Fork the repo, make your changes, and open a PR. Please include tests.
- 💬 **Need help?** Reach out on the [GenePattern Community Forum](https://groups.google.com/g/genepattern-help) or tag us in an issue.

```bash
# Get started with development
git clone https://github.com/genepattern/genepattern-mcp.git
cd genepattern-mcp
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
mcp dev server.py   # Explore all tools interactively
```

---

## Citing This Work

If GenePattern MCP accelerates your research, please cite the underlying GenePattern platform:

Reich M, Liefeld T, Gould J, Lerner J, Tamayo P, Mesirov JP. [GenePattern 2.0](http://www.nature.com/ng/journal/v38/n5/full/ng0506-500.html) Nature Genetics 38 no. 5 (2006): pp500-501 [Google Scholar](http://scholar.google.com/citations?user=lREO6vMAAAAJ&hl=en)

---

## License

Distributed under the **BSD 3-Clause License**. See [`LICENSE`](LICENSE) for details.

