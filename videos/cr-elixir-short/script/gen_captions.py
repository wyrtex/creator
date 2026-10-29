"""Builds compositions/captions.html from the per-scene voiceover word timings."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENE_START = {"s1": 0, "s2": 5, "s3": 9.7, "s4": 17.4, "s5": 23.2, "s6": 28.2, "s7": 31.7}
MAX_WORDS = 3

words = []
SKIP = {"s6"}  # the push scene is all type on a gold flood; captions would fight it
for sid, off in SCENE_START.items():
    if sid in SKIP:
        continue
    text = (ROOT / "script" / f"{sid}.txt").read_text(encoding="utf-8").split()
    tokens = [t for t in text if t not in ("—", "-")]
    timed = json.loads((ROOT / "assets" / "vo" / f"{sid}.json").read_text(encoding="utf-8"))
    assert len(tokens) == len(timed), (sid, tokens, [w["text"] for w in timed])
    for tok, w in zip(tokens, timed):  # match by position, keep the script's punctuation
        words.append({"text": tok, "start": off + w["start"], "end": off + w["end"], "stop": bool(re.search(r"[.?!,]$", tok))})

groups, cur = [], []
for i, w in enumerate(words):
    cur.append(w)
    nxt = words[i + 1] if i + 1 < len(words) else None
    if len(cur) >= MAX_WORDS or w["stop"] or nxt is None or nxt["start"] - w["end"] >= 0.15:
        groups.append(cur)
        cur = []

html_groups, tweens = [], []
for gi, g in enumerate(groups):
    start = round(g[0]["start"] - 0.05, 3)
    nxt_start = groups[gi + 1][0]["start"] - 0.05 if gi + 1 < len(groups) else g[-1]["end"] + 0.4
    end = round(min(g[-1]["end"] + 0.35, nxt_start), 3)
    gid = f"cap-{gi}"
    spans = " ".join(f'<span class="cap-w" id="{gid}-{wi}">{w["text"]}</span>' for wi, w in enumerate(g))
    html_groups.append(f'    <div class="cap-g clip" id="{gid}" data-start="{start}" data-duration="{round(end - start, 3)}">{spans}</div>')
    tweens.append(f'tl.fromTo("#{gid}", {{ opacity: 0, scale: 0.86 }}, {{ opacity: 1, scale: 1, duration: 0.12, ease: "back.out(2)" }}, {start});')
    for wi, w in enumerate(g):
        tweens.append(f'tl.fromTo("#{gid}-{wi}", {{ color: "#ffffff" }}, {{ color: "#ffc83a", duration: 0.05, ease: "none" }}, {round(w["start"], 3)});')
        if wi + 1 < len(g):
            tweens.append(f'tl.to("#{gid}-{wi}", {{ color: "#ffffff", duration: 0.05, ease: "none" }}, {round(g[wi + 1]["start"], 3)});')
    tweens.append(f'tl.to("#{gid}", {{ opacity: 0, duration: 0.08, ease: "power2.in" }}, {round(end - 0.08, 3)});')

total = max(SCENE_START.values()) + 5.5
out = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
    .cap-g {{
      position: absolute; left: 0; right: 0; top: 1170px; height: 150px; overflow: visible;
      display: flex; align-items: center; justify-content: center; gap: 0 18px; flex-wrap: wrap;
      padding: 0 110px; text-align: center;
      font-weight: 900; font-size: 66px; line-height: 1.05; letter-spacing: -0.01em; color: #ffffff;
      -webkit-text-stroke: 10px #070d2b; paint-order: stroke fill;
      text-shadow: 0 6px 18px rgba(0, 0, 0, 0.55);
    }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{chr(10).join(html_groups)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {chr(10) + "    ".join([""] + tweens)}
    window.__timelines["captions"] = tl;
  </script>
</template>
"""
(ROOT / "compositions" / "captions.html").write_text(out, encoding="utf-8")
print(len(words), "words,", len(groups), "groups")
