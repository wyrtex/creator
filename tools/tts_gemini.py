"""Voiceover with Gemini TTS (Google AI Studio, free tier) + word timings for captions.

usage: python3 tools/tts_gemini.py text.txt out.mp3 [--voice Fenrir] [--style "..."] [--model gemini-3.8-flash-tts]
needs GEMINI_API_KEY (aistudio.google.com -> Get API key). Writes out.mp3 and out.json (word timings).
Gemini returns no timings, so phrases are matched to the voiced stretches of the audio and words share them by syllables.
Tags like <short pause> or <laugh> in the text are performed, not captioned.
"""
import argparse, base64, json, os, re, ssl, subprocess, sys, tempfile, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from align_words import align_audio

API = "https://generativelanguage.googleapis.com/v1beta/interactions"
DEFAULT_STYLE = (
    "High-energy young male gaming YouTuber talking to his viewers: fast pace, punchy emphasis on numbers "
    "and key words, excited and confident, a little cheeky, conversational and natural. Not a newsreader."
)


def ssl_ctx():
    ca = os.environ.get("SSL_CERT_FILE") or ("/root/.ccr/ca-bundle.crt" if Path("/root/.ccr/ca-bundle.crt").exists() else None)
    return ssl.create_default_context(cafile=ca) if ca else ssl.create_default_context()


def find_audio(node):
    """Last base64 audio block anywhere in the response (steps[].content[] of type audio)."""
    found = None
    if isinstance(node, dict):
        if node.get("type") == "audio" and isinstance(node.get("data"), str):
            found = node["data"]
        for v in node.values():
            found = find_audio(v) or found
    elif isinstance(node, list):
        for v in node:
            found = find_audio(v) or found
    return found


def synth(text, voice, style, model, key):
    body = {
        "model": model,
        "input": [{"type": "user_input", "content": [
            {"type": "text", "text": text, "annotations": [{"type": "speech_metadata", "style": style}]}]}],
        "response_format": {"type": "audio"},
        "generation_config": {"speech_config": [{"voice": voice}]},
    }
    req = urllib.request.Request(API, data=json.dumps(body).encode(), method="POST",
                                 headers={"x-goog-api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, context=ssl_ctx(), timeout=180) as r:
            resp = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Gemini TTS {e.code}: {e.read().decode()[:600]}")
    data = find_audio(resp)
    if not data:
        sys.exit("no audio in response: " + json.dumps(resp)[:600])
    return base64.b64decode(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text_file"); ap.add_argument("out")
    ap.add_argument("--voice", default="Fenrir"); ap.add_argument("--style", default=DEFAULT_STYLE)
    ap.add_argument("--model", default="gemini-3.8-flash-tts")
    a = ap.parse_args()
    key = os.environ.get("GEMINI_API_KEY") or sys.exit("set GEMINI_API_KEY")
    text = Path(a.text_file).read_text(encoding="utf-8").strip()
    wav = synth(text, a.voice, a.style, a.model, key)
    out = Path(a.out)
    with tempfile.NamedTemporaryFile(suffix=".wav") as t:
        t.write(wav); t.flush()
        # trim leading/trailing silence, mp3 for the composition
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", t.name, "-af",
                        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,adelay=100",
                        "-ar", "44100", "-b:a", "192k", str(out)], check=True)
    words = align_audio(re.sub(r"<[^>]+>", " ", text), out)
    out.with_suffix(".json").write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out} ({len(words)} words)")


if __name__ == "__main__":
    main()
