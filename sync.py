"""CML Job: sync the project working tree to origin/main (public repo, no auth).

upload_file can't place files into subdirectories, so to pick up changes under
iceberg_mcp_server/ and notebooks/ we fetch + hard-reset to the remote. Untracked files
(e.g. ~/.local deps, logs) are left intact. Writes sync_log.txt for retrieval.
"""
import os
import subprocess

LOG = os.path.join(os.getcwd(), "sync_log.txt")


def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=os.getcwd())
    with open(LOG, "a") as f:
        f.write("$ " + " ".join(cmd) + "\n" + (p.stdout or "") + f"\n-> rc={p.returncode}\n\n")
    return p.returncode, p.stdout or ""


open(LOG, "w").close()
run(["git", "rev-parse", "--is-inside-work-tree"])
run(["git", "remote", "-v"])
run(["git", "fetch", "origin", "main"])
run(["git", "reset", "--hard", "origin/main"])
rc, out = run(["git", "log", "-1", "--oneline"])
with open(LOG, "a") as f:
    f.write("DONE\n")
print("sync done:", out.strip())
