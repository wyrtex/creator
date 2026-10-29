"""Small HTTP helpers shared by the uploaders (stdlib only, works behind the session proxy)."""
import json, os, ssl, sys, urllib.error, urllib.parse, urllib.request
from pathlib import Path

_CA = os.environ.get("SSL_CERT_FILE") or ("/root/.ccr/ca-bundle.crt" if Path("/root/.ccr/ca-bundle.crt").exists() else None)
CTX = ssl.create_default_context(cafile=_CA) if _CA else ssl.create_default_context()


def env(name):
    v = os.environ.get(name)
    if not v:
        sys.exit(f"missing env {name} (see tools/publish/README.md)")
    return v


def request(method, url, *, json_body=None, form=None, data=None, headers=None, timeout=600):
    """Returns (status, headers, parsed-json-or-text). Raises SystemExit on HTTP errors with the body."""
    headers = dict(headers or {})
    if json_body is not None:
        data = json.dumps(json_body).encode()
        headers.setdefault("Content-Type", "application/json; charset=UTF-8")
    elif form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
            raw = r.read()
            status, hdrs = r.status, dict(r.headers)
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {url.split('?')[0]} -> {e.code}: {e.read().decode(errors='replace')[:800]}")
    try:
        return status, hdrs, json.loads(raw) if raw else {}
    except ValueError:
        return status, hdrs, raw.decode(errors="replace")
