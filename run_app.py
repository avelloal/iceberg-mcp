"""CML Application entrypoint.

CML runs this script directly (and may run it under an IPython kernel with a live event
loop). To give the MCP server a clean process with its own loop, we subprocess-launch
serve_mcp.py with the same interpreter. This mirrors the proven collector/portal pattern.
"""
import os
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
# Vendored package lives at the project root; make it importable in the child.
env = dict(os.environ)
env["PYTHONPATH"] = HERE + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
env.setdefault("MCP_TRANSPORT", "http")

print(f"[run_app] launching serve_mcp.py (CDSW_APP_PORT={os.environ.get('CDSW_APP_PORT')})", flush=True)
proc = subprocess.run([sys.executable, os.path.join(HERE, "serve_mcp.py")], env=env)
sys.exit(proc.returncode)
