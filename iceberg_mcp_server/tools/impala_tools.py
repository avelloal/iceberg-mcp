## Copyright (c) 2025 Cloudera, Inc. All Rights Reserved.
##
## This file is licensed under the Apache License Version 2.0 (the "License").
## You may not use this file except in compliance with the License.
## You may obtain a copy of the License at http:##www.apache.org/licenses/LICENSE-2.0.
##
## This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
## OF ANY KIND, either express or implied. Refer to the License for the specific
## permissions and limitations governing your use of the file.

import json
import os
from impala.dbapi import connect

# --- MODIFIED from upstream (cloudera/iceberg-mcp-server @ 38a7f39) ---
# Credentials are supplied per-request by the MCP client via HTTP headers, so the deployed
# server holds no Impala secret. Precedence for each setting: request header -> env var ->
# default. Header names: X-Impala-User / -Password / -Host / -Port / -Database /
# -Auth-Mechanism / -Http-Path / -Use-Ssl / -Use-Http-Transport.
try:
    from fastmcp.server.dependencies import get_http_headers
except Exception:  # not running under HTTP transport, or older fastmcp
    def get_http_headers(include_all=False):  # type: ignore
        return {}


def _setting(headers, header_name, env_name, default):
    """Resolve one connection setting: HTTP header first, then env var, then default."""
    val = headers.get(header_name.lower())
    if val is None or val == "":
        val = os.getenv(env_name)
    return val if (val is not None and val != "") else default


# Helper to get Impala connection details from request headers, then env vars
def get_db_connection():
    headers = get_http_headers() or {}
    host = _setting(headers, "X-Impala-Host", "IMPALA_HOST", "coordinator-default-impala.example.com")
    port = int(_setting(headers, "X-Impala-Port", "IMPALA_PORT", "443"))
    user = _setting(headers, "X-Impala-User", "IMPALA_USER", "username")
    password = _setting(headers, "X-Impala-Password", "IMPALA_PASSWORD", "password")
    database = _setting(headers, "X-Impala-Database", "IMPALA_DATABASE", "default")
    auth_mechanism = _setting(headers, "X-Impala-Auth-Mechanism", "IMPALA_AUTH_MECHANISM", "LDAP")
    use_http_transport = _setting(headers, "X-Impala-Use-Http-Transport", "IMPALA_USE_HTTP_TRANSPORT", "true")
    http_path = _setting(headers, "X-Impala-Http-Path", "IMPALA_HTTP_PATH", "cliservice")
    use_ssl = _setting(headers, "X-Impala-Use-Ssl", "IMPALA_USE_SSL", "true")

    return connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        auth_mechanism=auth_mechanism,
        use_http_transport=use_http_transport,
        http_path=http_path,
        use_ssl=use_ssl,
    )


def execute_query(query: str) -> str:
    conn = None

    # Implement rudimentary SQL injection prevention
    # In this case, we only allow read-only queries
    # This is a very basic check and should be improved for production use
    readonly_prefixes = ["select", "show", "describe", "with"]

    if not query.strip().lower().split()[0] in readonly_prefixes:
        return "Only read-only queries are allowed."

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query)
        if cur.description:
            rows = cur.fetchall()
            result = json.dumps(rows, default=str)
        else:
            conn.commit()
            result = "Query executed successfully."
        cur.close()
        return result
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        # MODIFIED: guard close() — on a failed connection impyla's close() can raise
        # ("'NoneType' object has no attribute 'close'"), masking the real error (e.g. auth).
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


def get_schema() -> str:
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SHOW TABLES")
        tables = cur.fetchall()
        schema = [table[0] for table in tables]
        return json.dumps(schema)
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        # MODIFIED: guard close() — on a failed connection impyla's close() can raise
        # ("'NoneType' object has no attribute 'close'"), masking the real error (e.g. auth).
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
