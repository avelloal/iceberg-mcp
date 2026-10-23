"""Serve the vendored Cloudera iceberg-mcp-server over streamable HTTP.

Run as a clean `python serve_mcp.py` process (spawned by run_app.py) so it owns the
main thread and its own event loop — CML Application/Job scripts otherwise run under an
IPython kernel that already holds a running loop, which breaks uvicorn/anyio startup.

Binds 127.0.0.1:$CDSW_APP_PORT (loopback): the istio sidecar owns 0.0.0.0:$CDSW_APP_PORT
in CML, so binding 0.0.0.0 collides ("address already in use"). MCP endpoint: /mcp/.
"""
import os

# iceberg_mcp_server.server reads MCP_TRANSPORT; we force http and also pass it explicitly.
os.environ.setdefault("MCP_TRANSPORT", "http")

from iceberg_mcp_server.server import mcp  # module-level FastMCP; run() is guarded under __main__

port = int(os.environ.get("CDSW_APP_PORT", "8090"))
print(f"[serve_mcp] starting streamable-HTTP on 127.0.0.1:{port} (endpoint /mcp/)", flush=True)
mcp.run(transport="http", host="127.0.0.1", port=port)
