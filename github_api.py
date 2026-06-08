import os
import json
import urllib.request
import urllib.error
import time
from pathlib import Path

GITHUB_USER = "mayank-dev-15"
DATA_DIR = Path(__file__).parent / "data"
CACHE_FILE = DATA_DIR / ".etag_cache.json"

GRAPHQL_URL = "https://api.github.com/graphql"
REST_BASE = "https://api.github.com"


def get_token():
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        token = os.environ.get("GH_TOKEN", "")
    return token


def _load_cache():
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def _save_cache(cache):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache), encoding="utf-8")


def graphql_query(query, variables=None, token=None):
    if token is None:
        token = get_token()
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github+json",
    }
    req = urllib.request.Request(GRAPHQL_URL, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"GraphQL error {e.code}: {body[:500]}")
        raise


def rest_get(url, token=None, etag=None):
    if token is None:
        token = get_token()
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    if etag:
        headers["If-None-Match"] = etag
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8"), resp.headers.get("ETag"), resp.status
    except urllib.error.HTTPError as e:
        if e.code == 304:
            return None, etag, 304
        raise


def save_json(data, filename):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    filepath = DATA_DIR / filename
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return filepath


def load_json(filename):
    filepath = DATA_DIR / filename
    if filepath.exists():
        return json.loads(filepath.read_text(encoding="utf-8"))
    return None
