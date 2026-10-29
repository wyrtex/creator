"""One-time: get TIKTOK_REFRESH_TOKEN (valid 365 days).

1. python3 tools/publish/auth_tiktok.py url      -> open the printed link, allow access
2. you land on your redirect URI (the page may 404, that's fine): copy the whole address bar
3. python3 tools/publish/auth_tiktok.py code '<that address>'
env: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REDIRECT_URI (must match the one in the TikTok developer app)
"""
import sys, urllib.parse
from common import env, request

SCOPES = "user.info.basic,video.publish,video.upload"
if sys.argv[1:2] == ["url"]:
    q = urllib.parse.urlencode({"client_key": env("TIKTOK_CLIENT_KEY"), "scope": SCOPES, "response_type": "code",
                                "redirect_uri": env("TIKTOK_REDIRECT_URI"), "state": "creator"})
    print("https://www.tiktok.com/v2/auth/authorize/?" + q)
elif sys.argv[1:2] == ["code"]:
    code = urllib.parse.parse_qs(urllib.parse.urlparse(sys.argv[2]).query)["code"][0]
    _, _, t = request("POST", "https://open.tiktokapis.com/v2/oauth/token/", form={
        "client_key": env("TIKTOK_CLIENT_KEY"), "client_secret": env("TIKTOK_CLIENT_SECRET"), "code": code,
        "grant_type": "authorization_code", "redirect_uri": env("TIKTOK_REDIRECT_URI")})
    print("TIKTOK_REFRESH_TOKEN=" + t["refresh_token"])
else:
    sys.exit(__doc__)
