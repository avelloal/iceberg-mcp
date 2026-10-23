"""CML Application entrypoint.

Subprocess-launches serve_mcp.py (clean process / own event loop) and tees its combined
output to app_log.txt in the project root — CML exposes no application-logs API, so this is
how we retrieve startup errors.
"""
import os
import sys
import subprocess

# CML runs app scripts with __file__ undefined; the project root is the cwd.
HERE = os.getcwd()
LOG = open(os.path.join(HERE, "app_log.txt"), "w", buffering=1)


def w(m):
    LOG.write(m + "\n")
    print(m, flush=True)


env = dict(os.environ)
env["PYTHONPATH"] = HERE + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
env.setdefault("MCP_TRANSPORT", "http")

w(f"[run_app] python={sys.version.split()[0]} CDSW_APP_PORT={os.environ.get('CDSW_APP_PORT')}")
w(f"[run_app] launching {sys.executable} serve_mcp.py")
proc = subprocess.Popen(
    [sys.executable, os.path.join(HERE, "serve_mcp.py")],
    env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
)
for line in proc.stdout:
    LOG.write(line)
    sys.stdout.write(line)
    sys.stdout.flush()
proc.wait()
w(f"[run_app] child exited rc={proc.returncode}")
sys.exit(proc.returncode)
