"""Writes compositions/trade1.html and trade2.html from one layout (two elixir trades)."""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "compositions"

ICONS = {
    "horde": """
      <g transform="translate(58 78)"><path d="M-22 -4 L-48 -26 L-40 8 Z M22 -4 L48 -26 L40 8 Z" fill="#9ad0ff"/><circle r="26" fill="#3b7bff"/><circle cx="-9" cy="-4" r="6" fill="#fff"/><circle cx="9" cy="-4" r="6" fill="#fff"/></g>
      <g transform="translate(142 78)"><path d="M-22 -4 L-48 -26 L-40 8 Z M22 -4 L48 -26 L40 8 Z" fill="#9ad0ff"/><circle r="26" fill="#3b7bff"/><circle cx="-9" cy="-4" r="6" fill="#fff"/><circle cx="9" cy="-4" r="6" fill="#fff"/></g>
      <g transform="translate(100 146)"><path d="M-22 -4 L-48 -26 L-40 8 Z M22 -4 L48 -26 L40 8 Z" fill="#9ad0ff"/><circle r="26" fill="#3b7bff"/><circle cx="-9" cy="-4" r="6" fill="#fff"/><circle cx="9" cy="-4" r="6" fill="#fff"/></g>""",
    "arrows": """
      <g transform="rotate(-40 100 100)" stroke-linecap="round">
        <g><line x1="28" y1="62" x2="160" y2="62" stroke="#e8d3a8" stroke-width="9"/><path d="M152 46 L184 62 L152 78 Z" fill="#cfd8e6"/><path d="M28 62 L14 48 M28 62 L14 76" stroke="#ff5a6e" stroke-width="8"/></g>
        <g><line x1="28" y1="100" x2="160" y2="100" stroke="#e8d3a8" stroke-width="9"/><path d="M152 84 L184 100 L152 116 Z" fill="#cfd8e6"/><path d="M28 100 L14 86 M28 100 L14 114" stroke="#ff5a6e" stroke-width="8"/></g>
        <g><line x1="28" y1="138" x2="160" y2="138" stroke="#e8d3a8" stroke-width="9"/><path d="M152 122 L184 138 L152 154 Z" fill="#cfd8e6"/><path d="M28 138 L14 124 M28 138 L14 152" stroke="#ff5a6e" stroke-width="8"/></g>
      </g>""",
    "skeletons": """
      <g transform="translate(56 82)"><circle r="28" fill="#f1ede2"/><rect x="-16" y="16" width="32" height="20" rx="6" fill="#f1ede2"/><circle cx="-10" cy="-2" r="8" fill="#1b1730"/><circle cx="10" cy="-2" r="8" fill="#1b1730"/></g>
      <g transform="translate(144 82)"><circle r="28" fill="#f1ede2"/><rect x="-16" y="16" width="32" height="20" rx="6" fill="#f1ede2"/><circle cx="-10" cy="-2" r="8" fill="#1b1730"/><circle cx="10" cy="-2" r="8" fill="#1b1730"/></g>
      <g transform="translate(100 146)"><circle r="28" fill="#f1ede2"/><rect x="-16" y="16" width="32" height="20" rx="6" fill="#f1ede2"/><circle cx="-10" cy="-2" r="8" fill="#1b1730"/><circle cx="10" cy="-2" r="8" fill="#1b1730"/></g>""",
    "log": """
      <g transform="rotate(-18 100 100)">
        <rect x="18" y="66" width="150" height="68" rx="34" fill="#8b5a2b"/>
        <rect x="30" y="78" width="120" height="8" rx="4" fill="#6d4420"/><rect x="40" y="112" width="100" height="8" rx="4" fill="#6d4420"/>
        <ellipse cx="160" cy="100" rx="24" ry="34" fill="#e0ac72" stroke="#6d4420" stroke-width="6"/>
        <ellipse cx="160" cy="100" rx="11" ry="17" fill="none" stroke="#b27a42" stroke-width="5"/>
      </g>""",
}

def drop(id_, value, color):
    top, bot, edge = {"red": ("#ff9fae", "#c81e3a", "#5c0a1a"), "blue": ("#9fd3ff", "#1d6fd6", "#0a2a5c")}[color]
    return f"""<div class="drop" id="{id_}">
        <svg viewBox="0 0 92 112"><defs><linearGradient id="{id_}-g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/></linearGradient></defs>
          <path d="M46 4 C64 32 86 52 86 72 A40 40 0 0 1 6 72 C6 52 28 32 46 4 Z" fill="url(#{id_}-g)" stroke="{edge}" stroke-width="4"/></svg>
        <span>{value}</span>
      </div>"""

def scene(p):
    s = p["id"]
    a = p["at"]
    d = p["dur"]
    total = f'<div id="{s}-total" class="clip" data-start="{a["total"] - 0.05}" data-duration="{d - a["total"] + 0.05:.2f}">ВСЕГО <b>{p["total"]}</b></div>' if p.get("total") else ""
    total_tw = f'tl.fromTo("#{s}-total", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "expo.out" }}, {a["total"]});' if p.get("total") else ""
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
    #{s}-pill {{ position: absolute; top: 210px; left: 0; right: 0; text-align: center; }}
    #{s}-pill span {{
      display: inline-block; padding: 10px 26px; border-radius: 999px; background: rgba(255, 200, 58, 0.14);
      border: 2px solid rgba(255, 200, 58, 0.55); font-weight: 800; font-size: 30px; letter-spacing: 0.08em; color: var(--gold);
    }}
    .{s}-row {{ position: absolute; left: 0; right: 0; height: 330px; }}
    #{s}-opp {{ top: 290px; }}
    #{s}-you {{ top: 670px; }}
    .{s}-row .card {{ left: 120px; top: 0; }}
    .{s}-who {{ position: absolute; left: 430px; top: 34px; font-weight: 800; font-size: 34px; letter-spacing: 0.08em; }}
    .{s}-name {{ position: absolute; left: 430px; top: 84px; width: 600px; white-space: nowrap; font-weight: 900; font-size: 54px; line-height: 1.02; letter-spacing: -0.02em; }}
    .{s}-row .drop {{ left: 430px; top: 206px; }}
    .{s}-cost {{ position: absolute; left: 540px; top: 236px; font-weight: 800; font-size: 44px; color: var(--ink-dim); }}
    #{s}-shot {{ position: absolute; left: 175px; top: 640px; width: 160px; height: 160px; }}
    #{s}-result {{
      position: absolute; top: 1010px; left: 0; right: 0; text-align: center; line-height: 1;
    }}
    #{s}-result b {{
      font-weight: 900; font-size: 150px; letter-spacing: -0.04em; color: var(--win);
      text-shadow: 0 7px 0 #0f7a40, 0 0 60px rgba(65, 229, 138, 0.4);
    }}
    #{s}-result i {{ font-style: normal; font-weight: 800; font-size: 46px; color: var(--ink); margin-left: 18px; vertical-align: 34px; }}
    #{s}-total {{
      position: absolute; top: 236px; right: 60px; padding: 10px 22px; border-radius: 18px;
      background: rgba(65, 229, 138, 0.16); border: 2px solid rgba(65, 229, 138, 0.6); font-weight: 800; font-size: 34px;
    }}
    #{s}-total b {{ color: var(--win); }}
  </style>
  <div id="root" data-composition-id="{s}" data-width="1080" data-height="1920">
    <div id="{s}-pill" class="clip" data-start="0" data-duration="{d}"><span>{p["pill"]}</span></div>
    {total}
    <div id="{s}-opp" class="{s}-row clip" data-start="{a["opp"] - 0.05}" data-duration="{d - a["opp"] + 0.05:.2f}">
      <div class="card card--red" id="{s}-opp-card"><svg class="art" viewBox="0 0 200 200">{ICONS[p["opp_icon"]]}</svg><div class="card-name">{p["opp_short"]}</div></div>
      <div class="{s}-who" style="color: var(--red)">СОПЕРНИК</div>
      <div class="{s}-name">{p["opp_name"]}</div>
      {drop(f"{s}-opp-drop", p["opp_cost"], "red")}
      <div class="{s}-cost" id="{s}-opp-cost">эликсира</div>
    </div>
    <div id="{s}-you" class="{s}-row clip" data-start="{a["you"] - 0.05}" data-duration="{d - a["you"] + 0.05:.2f}">
      <div class="card" id="{s}-you-card"><svg class="art" viewBox="0 0 200 200">{ICONS[p["you_icon"]]}</svg><div class="card-name">{p["you_short"]}</div></div>
      <div class="{s}-who" style="color: var(--blue)">ТЫ</div>
      <div class="{s}-name">{p["you_name"]}</div>
      {drop(f"{s}-you-drop", p["you_cost"], "blue")}
      <div class="{s}-cost" id="{s}-you-cost">эликсира</div>
    </div>
    <svg id="{s}-shot" class="clip" data-start="{a["shot"] - 0.02}" data-duration="0.45" viewBox="0 0 200 200">{ICONS[p["you_icon"]]}</svg>
    <div id="{s}-result" class="clip" data-start="{a["result"] - 0.05}" data-duration="{d - a["result"] + 0.05:.2f}"><b>{p["result"]}</b><i>в твою пользу</i></div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#{s}-pill", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2, ease: "power2.out" }}, 0);
    // opponent's card lands, then its price
    tl.fromTo("#{s}-opp-card", {{ y: -120, rotation: -8, opacity: 0 }}, {{ y: 0, rotation: -3, opacity: 1, duration: 0.55, ease: "back.out(1.5)" }}, {a["opp"]});
    tl.fromTo("#{s}-opp .{s}-who, #{s}-opp .{s}-name", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.15, ease: "power4.out", stagger: 0.08 }}, {a["opp"] + 0.05});
    tl.fromTo("#{s}-opp-drop", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.4, ease: "back.out(2)" }}, {a["opp_cost"]});
    tl.fromTo("#{s}-opp-cost", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2, ease: "power2.out" }}, {a["opp_cost"] + 0.1});
    // your answer
    tl.fromTo("#{s}-you-card", {{ y: 120, rotation: 8, opacity: 0 }}, {{ y: 0, rotation: 3, opacity: 1, duration: 0.55, ease: "back.out(1.5)" }}, {a["you"]});
    tl.fromTo("#{s}-you .{s}-who, #{s}-you .{s}-name", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.15, ease: "power4.out", stagger: 0.08 }}, {a["you"] + 0.05});
    tl.fromTo("#{s}-you-drop", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.4, ease: "back.out(2)" }}, {a["you_cost"]});
    tl.fromTo("#{s}-you-cost", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2, ease: "power2.out" }}, {a["you_cost"] + 0.1});
    // your card's effect flies up and takes the opponent's card out
    tl.fromTo("#{s}-shot", {{ y: 0, scale: 0.8, opacity: 1 }}, {{ y: -360, scale: 1.1, opacity: 1, duration: 0.32, ease: "power3.in" }}, {a["shot"]});
    tl.to("#{s}-shot", {{ opacity: 0, scale: 1.6, duration: 0.1, ease: "power2.out" }}, {a["shot"] + 0.32});
    tl.fromTo("#{s}-opp-card", {{ filter: "brightness(1) grayscale(0)" }}, {{ filter: "brightness(2.2) grayscale(0)", duration: 0.06, ease: "none" }}, {a["shot"] + 0.32});
    tl.to("#{s}-opp-card", {{ filter: "brightness(0.5) grayscale(1)", duration: 0.35, ease: "power2.out" }}, {a["shot"] + 0.38});
    tl.fromTo("#{s}-opp", {{ x: 0 }}, {{ keyframes: [{{ x: -14 }}, {{ x: 12 }}, {{ x: -6 }}, {{ x: 0 }}], duration: 0.28, ease: "none" }}, {a["shot"] + 0.32});
    // the trade, in one number
    tl.fromTo("#{s}-result", {{ opacity: 0, scale: 1.6, filter: "blur(10px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.4, ease: "expo.out" }}, {a["result"]});
    {total_tw}
    tl.to(["#{s}-pill", "#{s}-opp", "#{s}-you", "#{s}-result"{', "#' + s + '-total"' if p.get("total") else ""}], {{ opacity: 0, filter: "blur(10px)", duration: 0.18, ease: "power2.in" }}, {d - 0.2});
    window.__timelines["{s}"] = tl;
  </script>
</template>
"""

TRADES = [
    dict(id="trade1", dur=7.7, pill="РАЗМЕН №1", opp_icon="horde", opp_short="Орда", opp_name="Орда миньонов", opp_cost=5,
         you_icon="arrows", you_short="Стрелы", you_name="Стрелы", you_cost=3, result="+2",
         at=dict(opp=1.19, opp_cost=2.08, you=3.95, you_cost=4.64, shot=5.0, result=5.84)),
    dict(id="trade2", dur=5.8, pill="РАЗМЕН №2", opp_icon="skeletons", opp_short="Армия", opp_name="Армия скелетов", opp_cost=3,
         you_icon="log", you_short="Бревно", you_name="Бревно", you_cost=2, result="+1", total="+3",
         at=dict(opp=0.10, opp_cost=1.15, you=2.22, you_cost=2.94, shot=3.4, result=4.12, total=4.63)),
]

for t in TRADES:
    (OUT / f"{t['id']}.html").write_text(scene(t), encoding="utf-8")
    print("wrote", t["id"])
