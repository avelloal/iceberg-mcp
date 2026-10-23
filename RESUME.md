# iceberg-mcp — RESUME

Deploy Cloudera's **iceberg-mcp-server** as a CML Application in `se-sandbox-aws-ml`, serving MCP
over **streamable HTTP**, backed by the **`xom-ice-kudu`** CDW Impala VW. Plus a test notebook.

Upstream: https://github.com/cloudera/iceberg-mcp-server (vendored at commit
`38a7f3914934ab851254291ed3a2934bcd95f6cd`, Apache-2.0). Two tools: `execute_query`, `get_schema`.

## Layout
```
iceberg_mcp_server/      vendored package (server.py exposes module-level `mcp` FastMCP)
serve_mcp.py             clean process: mcp.run(transport=http, host=127.0.0.1, port=$CDSW_APP_PORT)
run_app.py               CML Application entrypoint: subprocess-launches serve_mcp.py
bootstrap.py             CML Job: pip install --user deps + verify import
requirements.txt         fastmcp, impyla, mcp[cli], python-dotenv
notebooks/test_connection.ipynb   MCP client (fastmcp) — list_tools / get_schema / execute_query
state/impala.env         IMPALA_PASSWORD (gitignored)
```

## Backend (discovered via `cdp dw`)
- Env `se-sandbox-aws`, CDW cluster `env-h8cvm6`, Impala VW `xom-ice-kudu` (`impala-1792609196-cjs5`, Running).
- `IMPALA_HOST=coordinator-xom-ice-kudu.dw-se-sandbox-aws.a465-9q4k.cloudera.site` PORT 443
  httpPath `cliservice`, ssl, http transport, auth **LDAP** (workload user/pw). Supported: ldap/jwt/sso.
- `IMPALA_DATABASE=default`. **Credentials are NOT stored server-side** — the client passes
  `X-Impala-User`/`X-Impala-Password` (+ optional `-Host`/`-Database`) as HTTP headers per
  connection; `impala_tools.get_db_connection()` reads header → env → default. The app env only
  carries non-secret defaults (host/port/db/ssl/transport/auth) + `MCP_TRANSPORT=http`.

## Key decisions / gotchas
- Install deps directly (NOT the repo package): repo pins `requires-python>=3.13`; CML runtime is 3.11
  and the code runs fine on 3.11. Vendored package sits at project root (PYTHONPATH).
- App binds **127.0.0.1:$CDSW_APP_PORT** (loopback) — istio sidecar owns 0.0.0.0:$CDSW_APP_PORT.
- `run_app.py` subprocess-launches `serve_mcp.py` so the server gets a clean event loop
  (CML scripts run under an IPython kernel with a live loop → uvicorn/anyio would fail otherwise).
- MCP endpoint path: **`/mcp/`** (FastMCP streamable-HTTP default).
- App is behind Knox → clients send `Authorization: Bearer <CML APIv2 key>` (in-session: `CDSW_APIV2_KEY`).
- RISK to verify: Knox may buffer MCP SSE streaming; if so, test from an in-project CML Session.

## State (fill as deployed)
- CML project id: <tbd>
- Bootstrap job id: <tbd>
- Application subdomain / URL: <tbd>
