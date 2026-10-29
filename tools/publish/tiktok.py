"""Post a video to TikTok with the official Content Posting API (free).

python3 tools/publish/tiktok.py video.mp4 --caption-file c.txt [--mode direct|inbox] [--privacy PUBLIC_TO_EVERYONE]
  direct: posts straight away (until the app passes TikTok's audit, only SELF_ONLY on a private account works)
  inbox:  sends it to the TikTok app's inbox as a draft; you tap "Post" on the phone (scope video.upload)
env: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN (get it once with tools/publish/auth_tiktok.py)
"""
import argparse, json, math, os, time
from pathlib import Path
from common import env, request

API = "https://open.tiktokapis.com/v2"
CHUNK = 10 * 1024 * 1024


def access_token():
    _, _, t = request("POST", f"{API}/oauth/token/", form={
        "client_key": env("TIKTOK_CLIENT_KEY"), "client_secret": env("TIKTOK_CLIENT_SECRET"),
        "grant_type": "refresh_token", "refresh_token": env("TIKTOK_REFRESH_TOKEN")})
    if t.get("refresh_token") and t["refresh_token"] != os.environ.get("TIKTOK_REFRESH_TOKEN"):
        print(json.dumps({"note": "TikTok issued a new refresh token; store it", "TIKTOK_REFRESH_TOKEN": t["refresh_token"]}))
    return t["access_token"]


def chunks(size):
    n = size // CHUNK  # the last chunk absorbs the remainder (allowed up to 128 MB)
    return (size, 1) if n <= 1 else (CHUNK, n)


def post(path, caption, mode, privacy, cover_ms):
    tok = access_token()
    h = {"Authorization": f"Bearer {tok}"}
    size = os.path.getsize(path)
    chunk, n = chunks(size)
    source = {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": chunk, "total_chunk_count": n}
    if mode == "direct":
        _, _, info = request("POST", f"{API}/post/publish/creator_info/query/", json_body={}, headers=h)
        options = info["data"]["privacy_level_options"]
        if privacy not in options:
            print(json.dumps({"note": f"privacy {privacy} not allowed for this account/app, using {options[0]}", "options": options}))
            privacy = options[0]
        body = {"post_info": {"title": caption[:2200], "privacy_level": privacy, "disable_comment": False,
                              "disable_duet": False, "disable_stitch": False, "video_cover_timestamp_ms": cover_ms,
                              "is_aigc": True},
                "source_info": source}
        _, _, init = request("POST", f"{API}/post/publish/video/init/", json_body=body, headers=h)
    else:
        _, _, init = request("POST", f"{API}/post/publish/inbox/video/init/", json_body={"source_info": source}, headers=h)
    pid, url = init["data"]["publish_id"], init["data"]["upload_url"]
    raw = Path(path).read_bytes()
    for i in range(n):
        lo = i * chunk
        hi = size - 1 if i == n - 1 else lo + chunk - 1
        request("PUT", url, data=raw[lo:hi + 1], headers={"Content-Type": "video/mp4", "Content-Length": str(hi - lo + 1),
                                                           "Content-Range": f"bytes {lo}-{hi}/{size}"}, timeout=3600)
    status = None
    for _ in range(60):
        _, _, st = request("POST", f"{API}/post/publish/status/fetch/", json_body={"publish_id": pid}, headers=h)
        status = st["data"]["status"]
        if status in ("PUBLISH_COMPLETE", "SEND_TO_USER_INBOX"):
            break
        if status == "FAILED":
            raise SystemExit(f"tiktok failed: {st['data'].get('fail_reason')}")
        time.sleep(5)
    return {"platform": "tiktok", "publish_id": pid, "status": status, "mode": mode}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--caption-file")
    ap.add_argument("--mode", choices=["direct", "inbox"], default="direct")
    ap.add_argument("--privacy", default="PUBLIC_TO_EVERYONE"); ap.add_argument("--cover-ms", type=int, default=0)
    a = ap.parse_args()
    cap = Path(a.caption_file).read_text(encoding="utf-8") if a.caption_file else ""
    print(json.dumps(post(a.video, cap, a.mode, a.privacy, a.cover_ms), ensure_ascii=False))
