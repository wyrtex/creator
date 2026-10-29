---
name: channel-autopilot
description: Runs the Supercell YouTube channel end to end without a human - decides what and when to post (Shorts daily, one long video weekly), researches news or picks a strategy topic, writes the script, voices it, builds and renders the video, publishes to YouTube and cross-posts Shorts to Instagram Reels and TikTok, then logs and learns from stats. Use for "run the channel", "сделай сегодняшний ролик", "автопилот", scheduled daily runs, or "what should we post next".
---

# Channel autopilot

The channel is the product. Each run makes **one** finished video and publishes it, or says plainly why it did not.
Everything the run needs lives in the repo: `channel/config.json` (cadence, voice, mix), `channel/log.jsonl`
(what was made and published), `channel/backlog.md` (evergreen topics), `channel/plan.md` (this week's plan).
The container is wiped after the run: **commit and push** `channel/` and the new `videos/<slug>/` at the end of every run.

## 0. Preflight (stop early, never half-publish)

- Secrets present: `GEMINI_API_KEY`, `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`; for cross-posting
  `IG_USER_ID`, `IG_ACCESS_TOKEN`, `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_REFRESH_TOKEN`.
  A missing platform secret skips only that platform and is noted in the log.
- Read `channel/config.json`, the last 30 lines of `channel/log.jsonl`, `channel/plan.md` (if missing or older than
  7 days, do step 1 first).

## 1. Weekly plan (Mondays, or when `plan.md` is stale)

Use `yt-plan` sized to the cadence in config (default: 7 Shorts + 1 long a week). Inputs:
- `yt-viral`: what works in the niche right now on Russian-language Supercell YouTube, ranked by outlier score.
- Stats of our last videos: `python3 tools/publish/youtube.py --stats <ids from log>`; compare views at the same age.
  Keep doing what beats our median, drop what is under half of it (`yt-audit` reasoning).
- The content mix in config (news / strategy / tier list / facts) and game rotation: no game twice in a row unless
  there is big news for it.
Write `channel/plan.md`: one line per day - date, format, game, working title, angle, why.
The long video of the week is the deep version of the week's strongest Short topic; its best 2-3 moments become
next week's Shorts (`yt-shorts`).

## 2. Pick today's video

Today's slot comes from `plan.md`. **News overrides the plan**: search the last 72 hours (official Supercell game
blogs and X accounts, the games' subreddits, patch notes, Supercell's YouTube). A balance change, new
brawler/card/troop, season start or big event becomes today's Short (and moves the planned topic down).
Otherwise take the planned topic, then `backlog.md`.
Never repeat a topic already in `log.jsonl` within 30 days.

## 3. Facts

Every number, card cost, stat or date on screen traces to a source checked today (≥2 sources, or 1 official).
Leaks and rumours are labelled as such on screen ("СЛИВ", "ПО СЛУХАМ"). If a fact can't be confirmed, cut it.
Save the sources in `videos/<slug>/script/sources.md`.

## 4. Script

- Short (25-50 s): `short-form-video-script` + `hook-writer` (hook in the first second, frame 0 already shows it),
  one idea, one worked example, payoff before the swipe, one ask at the end.
- Long (6-10 min): `yt-script` (score the hook options, mark retention beats every 30-60 s), chapters by `yt-chapters`.
- Then `ig-human` on the spoken text: no AI slop words, no em-dash pile-ups; write numbers as words for the voice
  ("пять", not "5"). One sentence per line, split into scene files `s1.txt … sN.txt`.

## 5. Voice

`python3 tools/tts_gemini.py sN.txt assets/vo/sN.mp3` per scene (voice and style from config; default Fenrir,
high-energy gaming YouTuber). Writes word timings `sN.json` for captions. Angle tags such as `<short pause>`,
`<laugh>` are performed, not captioned; use them sparingly on the hook and the payoff.
On a Gemini error or quota hit: retry once with `fallback_voice`, then fall back to `python3 tools/tts.py`
(edge-tts) and note it in the log.

## 6. Video

Start from the reference project `videos/cr-elixir-short/` (vertical) - copy it to `videos/<date>-<slug>/` and
rebuild scenes for the new script. Follow `/hyperframes` (contract, vertical safe zones, motion, captions) and the
taste skills (`emil-design-eng`, `design-taste-frontend`): every scene has an object that explains the line
(cards, bars, maps of the arena/base, counters), never bullet slides. Vary scene entrances between videos.
Long videos: 1920×1080, one sub-composition per chapter, and a thumbnail composition rendered as a PNG
(`npx hyperframes snapshot`), packaged with `yt-package` (title + thumbnail as one pairing).
Gate before render: `npx hyperframes check --json` with 0 errors, then snapshots of every scene's midpoint, looked at.
Render `--quality delivery` to `output/<date>-<slug>/video.mp4`; verify duration with ffprobe and loudness with
`npx hyperframes audio --json` (−16…−14 LUFS, true peak ≤ −1 dB; else `npx hyperframes normalize-audio`).
No game art you don't have rights to; draw it. No unlicensed music.

## 7. Publish

Text per platform into `output/<date>-<slug>/meta.json`: YouTube title (`yt-package`), description and tags
(`yt-seo`, chapters for long videos), IG caption (`ig-caption`), TikTok caption (search keyword first). Every
description ends with the Supercell disclaimer from config.

- YouTube: `python3 tools/publish/youtube.py video.mp4 --title ... --description-file ... --tags ... --publish-at <slot time in UTC>`
  (Shorts: vertical and ≤ 3 min is enough; add `#shorts` to the title or description).
- Shorts only, after the YouTube upload succeeded:
  `python3 tools/publish/instagram.py video.mp4 --caption-file ig.txt` and
  `python3 tools/publish/tiktok.py video.mp4 --caption-file tt.txt --mode <tiktok_mode from config>`.
  If TikTok prints a new refresh token, say so in the run summary (the environment secret must be updated).
- Publish at the slot time: upload YouTube with `--publish-at`; for IG/TikTok (no scheduling) run the post step
  when the run happens at slot time (the daily schedule is set to fire shortly before it).

## 8. Log and learn

Append one JSON line to `channel/log.jsonl`: date, slot, format, game, topic, hook, output path, voice used,
each platform's id/url/status, and anything skipped. Every Sunday, pull stats for the week, write three lines of
lessons at the top of `channel/plan.md` (what to repeat, what to stop, one experiment), then make next week's plan.
Commit (`channel: <date> <slug>`) and push.

## Never

- Publish a video that failed `check`, has an unverified fact, or uses copyrighted music/art.
- Pose as Supercell or an official channel; use the Supercell logo as our branding.
- Post more than the cadence; one good video beats two rushed ones.
- Engage in fake engagement (bought views, sock-puppet comments).
