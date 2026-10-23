"""Serve the vendored Cloudera iceberg-mcp-server over streamable HTTP.

Launched as a clean `python serve_mcp.py` by run_app.py so it owns the main thread and its own
event loop (CML scripts otherwise run under an IPython kernel with a live loop). Binds
127.0.0.1:$CDSW_APP_PORT (loopback; istio sidecar owns 0.0.0.0:$CDSW_APP_PORT). Endpoint: /mcp/.
"""
import os
import sys
import traceback

os.environ.setdefault("MCP_TRANSPORT", "http")

try:
    import fastmcp
    from iceberg_mcp_server.server import mcp

    port = int(os.environ.get("CDSW_APP_PORT", "8090"))
    print(f"[serve_mcp] fastmcp={fastmcp.__version__} binding 127.0.0.1:{port} endpoint=/mcp/", flush=True)
    mcp.run(transport="http", host="127.0.0.1", port=port)
except Exception:
    print("[serve_mcp] FAILED to start:\n" + traceback.format_exc(), flush=True)
    sys.exit(1)
