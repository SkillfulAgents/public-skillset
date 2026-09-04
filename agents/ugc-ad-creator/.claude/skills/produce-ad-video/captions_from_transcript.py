# /// script
# requires-python = ">=3.10"
# dependencies = ["faster-whisper"]
# ///
"""Transcribe talking-head clips with word timestamps and emit Remotion caption props.

Usage:
  uv run captions_from_transcript.py \
    --clip head-A.mp4:0.0 --clip head-B.mp4:6.8 \
    --emphasis busywork,agent,sleep \
    --max-chars 16 --out props-captions.json

Each --clip is <path>:<offset-seconds-in-composition>. Output is
{"captions": [{text, start, end, emphasis}]} ready to merge into input props.
"""
import argparse
import json
import re


def group_words(words, max_chars, emphasis):
    groups = []
    cur = []

    def flush():
        if not cur:
            return
        text = " ".join(w["text"] for w in cur)
        emph = any(re.sub(r"[^\w]", "", w["text"]).lower() in emphasis for w in cur)
        groups.append({
            "text": text,
            "start": cur[0]["start"],
            "end": cur[-1]["end"],
            "emphasis": emph,
        })
        cur.clear()

    for w in words:
        clean = re.sub(r"[^\w]", "", w["text"]).lower()
        is_emph = clean in emphasis
        candidate = " ".join(x["text"] for x in cur + [w])
        if cur and (len(candidate) > max_chars or is_emph or cur[-1].get("_emph")):
            flush()
        w = dict(w, _emph=is_emph)
        cur.append(w)
        if w["text"].rstrip().endswith((".", ",", "!", "?")):
            flush()
    flush()
    # close gaps: extend each caption to the start of the next
    for a, b in zip(groups, groups[1:]):
        if 0 < b["start"] - a["end"] < 0.6:
            a["end"] = b["start"]
    for g in groups:
        g.pop("_emph", None)
    return groups


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clip", action="append", required=True, help="<path>:<offset-sec>")
    ap.add_argument("--emphasis", default="")
    ap.add_argument("--max-chars", type=int, default=16)
    ap.add_argument("--model", default="base.en")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    from faster_whisper import WhisperModel

    m = WhisperModel(args.model, device="cpu", compute_type="int8")
    emphasis = {e.strip().lower() for e in args.emphasis.split(",") if e.strip()}

    captions = []
    for spec in args.clip:
        path, off = spec.rsplit(":", 1)
        off = float(off)
        segs, _ = m.transcribe(path, word_timestamps=True)
        words = [
            {"text": w.word.strip(), "start": round(w.start + off, 3), "end": round(w.end + off, 3)}
            for s in segs
            for w in s.words
        ]
        print(f"{path}: {' '.join(w['text'] for w in words)}")
        captions.extend(group_words(words, args.max_chars, emphasis))

    json.dump({"captions": captions}, open(args.out, "w"), indent=1)
    print(f"wrote {len(captions)} captions -> {args.out}")


if __name__ == "__main__":
    main()
