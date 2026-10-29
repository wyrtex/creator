"""One-time: get YT_REFRESH_TOKEN via Google's device flow (open a URL on any device, type the code).

Needs an OAuth client of type "TVs and Limited Input devices" in Google Cloud Console (YouTube Data API v3 enabled).
env: YT_CLIENT_ID, YT_CLIENT_SECRET
"""
import json, time, urllib.error, urllib.parse, urllib.request
from common import CTX, env, request

SCOPE = "https://www.googleapis.com/auth/youtube"
_, _, dev = request("POST", "https://oauth2.googleapis.com/device/code", form={"client_id": env("YT_CLIENT_ID"), "scope": SCOPE})
print(f"Open {dev['verification_url']} and enter code: {dev['user_code']}", flush=True)
body = urllib.parse.urlencode({"client_id": env("YT_CLIENT_ID"), "client_secret": env("YT_CLIENT_SECRET"),
                               "device_code": dev["device_code"], "grant_type": "urn:ietf:params:oauth:grant-type:device_code"}).encode()
while True:
    time.sleep(dev.get("interval", 5))
    try:  # polled by hand: "authorization_pending" comes back as an HTTP 428 we must not exit on
        with urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", data=body), context=CTX) as r:
            print("YT_REFRESH_TOKEN=" + json.load(r)["refresh_token"])
            break
    except urllib.error.HTTPError as e:
        err = json.loads(e.read() or b"{}").get("error")
        if err not in ("authorization_pending", "slow_down"):
            raise SystemExit(f"auth failed: {err}")
