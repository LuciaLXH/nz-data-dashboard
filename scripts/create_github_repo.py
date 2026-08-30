"""Create the private GitHub repo + STATS_NZ_API_KEY Actions secret.

Usage (token stays in the environment, never on the command line):
    GH_TOKEN=<personal-access-token> \
    STATS_NZ_API_KEY=$(grep STATS_NZ_API_KEY .env | cut -d= -f2) \
    .venv/bin/python scripts/create_github_repo.py

Steps:
  1. POST /user/repos            → private repo `nz-data-dashboard`
  2. GET  /repos/.../actions/secrets/public-key
  3. PUT  /repos/.../actions/secrets/STATS_NZ_API_KEY  (libsodium sealed box)

Prints the origin URL for `git remote add origin <url>` (or adds it).
Never prints the token or the secret value.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import urllib.request

import nacl.public
import nacl.encoding

API = "https://api.github.com"
REPO_NAME = "nz-data-dashboard"
REPO_DESC = ("NZ water dashboard: population growth vs council water supply "
             "pressure (6 regions) — static site, CC BY 4.0 data")


def _req(method: str, url: str, token: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:400]
        raise SystemExit(f"GitHub API {e.code} on {method} {url}: {detail}")


def main() -> int:
    token = os.environ.get("GH_TOKEN", "").strip()
    if not token:
        raise SystemExit("GH_TOKEN is not set — pass a Personal Access Token "
                         "(scope: repo) via the environment.")
    api_key = os.environ.get("STATS_NZ_API_KEY", "").strip()
    if not api_key:
        print("WARNING: STATS_NZ_API_KEY not set — repo will be created but the "
              "Actions secret will be skipped (add it manually in Settings → "
              "Secrets and variables → Actions).", file=sys.stderr)

    # 1. create the private repo
    user = _req("GET", f"{API}/user", token)
    owner = user["login"]
    try:
        repo = _req("POST", f"{API}/user/repos", token, {
            "name": REPO_NAME, "private": True,
            "description": REPO_DESC,
            "has_issues": True, "has_wiki": False,
        })
    except SystemExit as e:
        if "already exists" in str(e):
            print(f"repo {owner}/{REPO_NAME} already exists — using it.")
            repo = {"full_name": f"{owner}/{REPO_NAME}"}
        else:
            raise
    print(f"✅ repo: https://github.com/{repo['full_name']}")

    # 2+3. Actions secret (only if key provided)
    if api_key:
        pk = _req("GET", f"{API}/repos/{owner}/{REPO_NAME}/actions/secrets/public-key", token)
        pub = nacl.public.PublicKey(pk["key"], nacl.encoding.Base64Encoder)
        box = nacl.public.SealedBox(pub)
        encrypted = box.encrypt(api_key.encode())
        _req("PUT", f"{API}/repos/{owner}/{REPO_NAME}/actions/secrets/STATS_NZ_API_KEY",
             token, {
                 "encrypted_value": base64.b64encode(encrypted).decode(),
                 "key_id": pk["key_id"],
             })
        print("✅ Actions secret STATS_NZ_API_KEY configured")

    origin = f"https://github.com/{owner}/{REPO_NAME}.git"
    print(f"\nNext:  git remote add origin {origin}\n       git push -u origin main")
    return 0


if __name__ == "__main__":
    sys.exit(main())
