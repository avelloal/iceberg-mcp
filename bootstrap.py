"""CML Job: install the MCP server's runtime deps into the project, with full diagnostics.

Writes everything to bootstrap_log.txt in the project root (downloadable via the API) because
CML exposes no job-logs endpoint. Handles the known PBJ pip gotchas: a runtime-set PIP_TARGET
conflicts with `pip install --user`, so we detect and avoid that.
"""
import os
import sys
import subprocess
import traceback

LOG = os.path.join(os.getcwd(), "bootstrap_log.txt")
DEPS = ["fastmcp>=2.9.2", "impyla>=0.21.0", "mcp[cli]>=1.9.4", "python-dotenv>=1.1.0"]


def log(*a):
    line = " ".join(str(x) for x in a)
    with open(LOG, "a") as f:
        f.write(line + "\n")
    print(line, flush=True)


def run(cmd):
    log("$", " ".join(cmd))
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    log(p.stdout[-6000:] if p.stdout else "(no output)")
    log("-> returncode", p.returncode)
    return p.returncode


def main():
    open(LOG, "w").close()
    log("=== bootstrap diagnostics ===")
    log("python:", sys.version.replace("\n", " "))
    log("executable:", sys.executable)
    log("cwd:", os.getcwd())
    log("cwd listing:", sorted(os.listdir("."))[:40])
    for k in ("PIP_TARGET", "PIP_USER", "PIP_PREFIX", "PYTHONPATH", "PIP_REQUIRE_VIRTUALENV"):
        log(f"env {k}:", os.environ.get(k))

    # Avoid the --user vs PIP_TARGET conflict: if the runtime pins PIP_TARGET, install there;
    # otherwise use --user (persists in /home/cdsw/.local for the Application).
    pip = [sys.executable, "-m", "pip", "install", "--upgrade"]
    if os.environ.get("PIP_TARGET"):
        log("PIP_TARGET set -> installing to it (no --user)")
        rc = run(pip + DEPS)
    else:
        rc = run(pip + ["--user"] + DEPS)
        if rc != 0:
            log("retry without --user")
            rc = run(pip + DEPS)

    log("=== import verification ===")
    status = "OK"
    for mod in ("fastmcp", "impala.dbapi", "mcp", "dotenv", "iceberg_mcp_server.server"):
        try:
            __import__(mod)
            log("import OK:", mod)
        except Exception:
            status = "IMPORT_FAIL"
            log("import FAIL:", mod)
            log(traceback.format_exc())

    try:
        import fastmcp
        from iceberg_mcp_server.server import mcp
        log("fastmcp", getattr(fastmcp, "__version__", "?"), "| server:", mcp.name)
    except Exception:
        log(traceback.format_exc())

    log("pip_returncode", rc)
    log("FINAL_STATUS", "OK" if (rc == 0 and status == "OK") else f"FAIL(pip={rc},{status})")


main()
