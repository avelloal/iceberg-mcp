# iceberg-mcp (CML deployment)

Deploys Cloudera's [iceberg-mcp-server](https://github.com/cloudera/iceberg-mcp-server)
(Apache-2.0; vendored under `iceberg_mcp_server/` at commit `38a7f39`) as a **Cloudera AI
Application**, serving MCP over **streamable HTTP** (`/mcp/`), backed by a CDW **Impala**
Virtual Warehouse. A test notebook exercises the two tools (`get_schema`, `execute_query`).

See [RESUME.md](RESUME.md) for architecture, backend endpoint, decisions, and gotchas.

## Files
- `iceberg_mcp_server/` — vendored upstream package (unmodified)
- `serve_mcp.py` — runs the FastMCP server on `127.0.0.1:$CDSW_APP_PORT`
- `run_app.py` — CML Application entrypoint (subprocess-launches `serve_mcp.py`)
- `bootstrap.py` — CML Job: `pip install --user` the deps
- `notebooks/test_connection.ipynb` — MCP client connection test
- `state/` — gitignored (holds `impala.env` = workload password)

Credentials come from environment / CML project env vars; none are committed.
