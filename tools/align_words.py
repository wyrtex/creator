"""Time the script's own words using a transcript's word timings (whisper spells numbers as digits, drops dashes)."""
import difflib, re

NUM = {"0": "ноль", "1": "один", "2": "два", "3": "три", "4": "четыре", "5": "пять", "6": "шесть", "7": "семь", "8": "восемь", "9": "девять", "10": "десять"}


def norm(w):
    w = re.sub(r"[^\w-]", "", w.lower().replace("ё", "е")).strip("-")
    return NUM.get(w, w)


def align(text, heard):
    """text: script string; heard: [{text,start,end}]. Returns [{text,start,end}] for every script word, in order."""
    tokens = [t for t in text.split() if norm(t)]
    a, b = [norm(t) for t in tokens], [norm(w["text"]) for w in heard]
    times = [None] * len(tokens)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            h = heard[blk.b + k]
            times[blk.a + k] = (h["start"], h["end"])
    # unmatched words share the gap between their matched neighbours
    i = 0
    while i < len(times):
        if times[i] is not None:
            i += 1; continue
        j = i
        while j < len(times) and times[j] is None:
            j += 1
        lo = times[i - 1][1] if i > 0 else (heard[0]["start"] if heard else 0.0)
        hi = times[j][0] if j < len(times) else (heard[-1]["end"] if heard else lo + 0.4 * (j - i))
        hi = max(hi, lo + 0.05 * (j - i))
        step = (hi - lo) / (j - i)
        for k in range(i, j):
            times[k] = (lo + step * (k - i), lo + step * (k - i + 1))
        i = j
    return [{"text": t, "start": round(s, 3), "end": round(e, 3)} for t, (s, e) in zip(tokens, times)]


VOWELS = set("аеёиоуыэюяaeiouy")


def speech_spans(audio, noise="-35dB", min_pause=0.22):
    """[(start, end)] of voiced stretches, from ffmpeg silencedetect."""
    import subprocess
    err = subprocess.run(["ffmpeg", "-i", str(audio), "-af", f"silencedetect=noise={noise}:d={min_pause}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    h, m, sec = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err).groups()
    dur = int(h) * 3600 + int(m) * 60 + float(sec)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    spans, cur = [], 0.0
    for s, e in zip(starts, ends + [dur] * (len(starts) - len(ends))):
        if s - cur > 0.05:
            spans.append((cur, s))
        cur = e
    if dur - cur > 0.05:
        spans.append((cur, dur))
    return spans


def weight(tok):
    return max(1, sum(c in VOWELS for c in tok.lower())) + 0.3


def align_audio(text, audio, heard=None):
    """Phrases (split at . ? ! … and ,) are matched to voiced stretches; words share their stretch by syllables.
    When the counts disagree, phrases are merged greedily by length; with a transcript, falls back to align()."""
    tokens = [t for t in text.split() if norm(t)]
    phrases, cur = [], []
    for t in tokens:
        cur.append(t)
        if re.search(r"[.?!…,:;]$", t):
            phrases.append(cur); cur = []
    if cur:
        phrases.append(cur)
    spans = speech_spans(audio)
    if len(spans) > len(phrases):  # a breath inside a phrase: join the closest stretches
        while len(spans) > len(phrases):
            gaps = [spans[i + 1][0] - spans[i][1] for i in range(len(spans) - 1)]
            i = gaps.index(min(gaps))
            spans[i:i + 2] = [(spans[i][0], spans[i + 1][1])]
    while len(phrases) > len(spans):  # no pause at a comma: join the shortest neighbouring phrases
        i = min(range(len(phrases) - 1), key=lambda k: len(phrases[k]) + len(phrases[k + 1]))
        phrases[i:i + 2] = [phrases[i] + phrases[i + 1]]
    out = []
    for words, (s, e) in zip(phrases, spans):
        ws = [weight(w) for w in words]
        t, k = s, (e - s) / sum(ws)
        for w, wt in zip(words, ws):
            out.append({"text": w, "start": round(t, 3), "end": round(t + wt * k, 3)})
            t += wt * k
    return out
