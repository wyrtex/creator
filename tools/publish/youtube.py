"""Upload to YouTube with the Data API v3 (free quota: ~6 uploads/day).

python3 tools/publish/youtube.py video.mp4 --title "..." --description-file d.txt --tags a,b \
    [--publish-at 2026-11-01T15:00:00Z] [--privacy public|unlisted|private] [--thumbnail t.png] [--made-for-kids]
python3 tools/publish/youtube.py --stats VIDEO_ID[,VIDEO_ID...]     # views/likes/comments, for the autopilot
env: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (get it once with tools/publish/auth_youtube.py)
"""
import argparse, json, os, sys
from pathlib import Path
from common import env, request


def access_token():
    _, _, tok = request("POST", "https://oauth2.googleapis.com/token", form={
        "client_id": env("YT_CLIENT_ID"), "client_secret": env("YT_CLIENT_SECRET"),
        "refresh_token": env("YT_REFRESH_TOKEN"), "grant_type": "refresh_token"})
    return tok["access_token"]


def upload(path, title, description, tags, privacy, publish_at, kids, category="20"):  # 20 = Gaming
    tok = access_token()
    size = os.path.getsize(path)
    status = {"privacyStatus": "private" if publish_at else privacy, "selfDeclaredMadeForKids": kids}
    if publish_at:
        status["publishAt"] = publish_at  # YouTube flips it to public at this time
    meta = {"snippet": {"title": title[:100], "description": description[:5000], "tags": tags,
                        "categoryId": category, "defaultLanguage": "ru", "defaultAudioLanguage": "ru"},
            "status": status}
    _, hdrs, _ = request("POST", "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                         json_body=meta, headers={"Authorization": f"Bearer {tok}", "X-Upload-Content-Type": "video/mp4",
                                                  "X-Upload-Content-Length": str(size)})
    loc = hdrs.get("Location") or hdrs.get("location")
    _, _, video = request("PUT", loc, data=Path(path).read_bytes(),
                          headers={"Authorization": f"Bearer {tok}", "Content-Type": "video/mp4"}, timeout=3600)
    return tok, video


def set_thumbnail(tok, video_id, png):
    ctype = "image/png" if png.endswith(".png") else "image/jpeg"
    request("POST", f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={video_id}",
            data=Path(png).read_bytes(), headers={"Authorization": f"Bearer {tok}", "Content-Type": ctype})


def stats(ids):
    tok = access_token()
    _, _, r = request("GET", f"https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet&id={ids}",
                      headers={"Authorization": f"Bearer {tok}"})
    return [{"id": v["id"], "title": v["snippet"]["title"], "published": v["snippet"]["publishedAt"], **v["statistics"]}
            for v in r.get("items", [])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", nargs="?"); ap.add_argument("--title"); ap.add_argument("--description-file")
    ap.add_argument("--tags", default=""); ap.add_argument("--privacy", default="public")
    ap.add_argument("--publish-at"); ap.add_argument("--thumbnail"); ap.add_argument("--made-for-kids", action="store_true")
    ap.add_argument("--stats")
    a = ap.parse_args()
    if a.stats:
        print(json.dumps(stats(a.stats), ensure_ascii=False, indent=1)); return
    if not (a.video and a.title):
        sys.exit("video and --title are required")
    desc = Path(a.description_file).read_text(encoding="utf-8") if a.description_file else ""
    tok, video = upload(a.video, a.title, desc, [t for t in a.tags.split(",") if t], a.privacy, a.publish_at, a.made_for_kids)
    if a.thumbnail:
        set_thumbnail(tok, video["id"], a.thumbnail)
    print(json.dumps({"platform": "youtube", "id": video["id"], "url": f"https://youtu.be/{video['id']}",
                      "privacy": video["status"]["privacyStatus"], "publishAt": video["status"].get("publishAt")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
