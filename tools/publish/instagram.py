"""Publish a Reel to Instagram with the Graph API (free). Resumable upload from a local file.

python3 tools/publish/instagram.py video.mp4 --caption-file c.txt [--cover-offset-ms 1500]
env: IG_USER_ID (Instagram professional account id), IG_ACCESS_TOKEN (Facebook Login for Business token with
     instagram_basic, instagram_content_publish, pages_show_list; a System User token does not expire)
"""
import argparse, json, os, time
from pathlib import Path
from common import env, request

V = "v21.0"
GRAPH = f"https://graph.facebook.com/{V}"


def publish(path, caption, thumb_offset_ms):
    uid, tok = env("IG_USER_ID"), env("IG_ACCESS_TOKEN")
    auth = {"Authorization": f"OAuth {tok}"}
    _, _, c = request("POST", f"{GRAPH}/{uid}/media", form={
        "media_type": "REELS", "upload_type": "resumable", "caption": caption[:2200],
        "share_to_feed": "true", "thumb_offset": str(thumb_offset_ms), "access_token": tok})
    cid = c["id"]
    request("POST", f"https://rupload.facebook.com/ig-api-upload/{V}/{cid}", data=Path(path).read_bytes(),
            headers={**auth, "offset": "0", "file_size": str(os.path.getsize(path))}, timeout=3600)
    for _ in range(60):  # processing usually takes 10-60 s
        _, _, st = request("GET", f"{GRAPH}/{cid}?fields=status_code,status", headers=auth)
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") in ("ERROR", "EXPIRED"):
            raise SystemExit(f"instagram processing failed: {st}")
        time.sleep(5)
    _, _, pub = request("POST", f"{GRAPH}/{uid}/media_publish", form={"creation_id": cid}, headers=auth)
    _, _, m = request("GET", f"{GRAPH}/{pub['id']}?fields=permalink", headers=auth)
    return {"platform": "instagram", "id": pub["id"], "url": m.get("permalink")}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--caption-file"); ap.add_argument("--cover-offset-ms", type=int, default=0)
    a = ap.parse_args()
    cap = Path(a.caption_file).read_text(encoding="utf-8") if a.caption_file else ""
    print(json.dumps(publish(a.video, cap, a.cover_offset_ms), ensure_ascii=False))
