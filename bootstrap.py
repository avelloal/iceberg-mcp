"""CML Job: install the MCP server's runtime deps into the project's persistent ~/.local.

Installs to --user (/home/cdsw/.local) so the Application picks them up. We install the
deps directly (NOT `pip install` of the repo package, whose requires-python>=3.13 would
reject the 3.11 runtime); the vendored iceberg_mcp_server package runs fine on 3.11.

Import-guard first so re-runs are fast and we avoid the `pip --target skips existing` trap.
"""
import subprocess
import sys

DEPS = ["fastmcp>=2.9.2", "impyla>=0.21.0", "mcp[cli]>=1.9.4", "python-dotenv>=1.1.0"]


def have_deps() -> bool:
    try:
        import fastmcp  # noqa: F401
        import impala.dbapi  # noqa: F401  (impyla)
        import mcp  # noqa: F401
        import dotenv  # noqa: F401
        return True
    except Exception:
        return False


def main():
    if have_deps():
        print("[bootstrap] deps already importable; skipping install")
    else:
        print("[bootstrap] installing:", DEPS, flush=True)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--upgrade", *DEPS])

    # Verify the vendored server imports and the tools are registered.
    from iceberg_mcp_server.server import mcp
    import fastmcp, impala, mcp as mcp_pkg
    print("[bootstrap] versions:",
          "fastmcp", getattr(fastmcp, "__version__", "?"),
          "| mcp", getattr(mcp_pkg, "__version__", "?"))
    print("[bootstrap] FastMCP server name:", mcp.name)
    print("[bootstrap] OK — ready to serve")


main()  # __name__ is not reliably "__main__" in CML jobs
