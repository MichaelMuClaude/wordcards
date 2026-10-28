"""Step 2: apply the hand review (data/review/*.txt) to the candidates and write data/cards.tsv.

    python scripts/02_build_cards.py

Review file format, one per letter (a.txt ... z.txt):
    KEEP: word word ...        only these words of that letter are kept
    REMOVE: word word ...      (instead of KEEP) every word except these is kept
    HINT: word=prompt text     how to draw the word; a leading "!" forces a scene-style prompt
data/review/extra.txt holds later fixes: REMOVE lines and HINT lines that override the letter files.
"""

import argparse
import csv
import json
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ipa import ipa  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def parse(path):
    keep, remove, hints = None, set(), {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("KEEP:"):
            keep = set(line[5:].split())
        elif line.startswith("REMOVE:"):
            remove |= set(line[7:].split())
        elif line.startswith("HINT:"):
            k, v = line[5:].strip().split("=", 1)
            hints[k.strip()] = v.strip()
    return keep, remove, hints


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", default=ROOT / "data/candidates_rank20000.tsv")
    ap.add_argument("--review", default=ROOT / "data/review")
    ap.add_argument("--zh", default=ROOT / "data/zh.json")
    ap.add_argument("--out", default=ROOT / "data/cards.tsv")
    args = ap.parse_args()

    cand = {r["word"]: r for r in csv.DictReader(open(args.candidates, encoding="utf-8"), delimiter="\t")}
    zh = json.load(open(args.zh, encoding="utf-8"))
    review = Path(args.review)
    _, extra_remove, extra_hints = parse(review / "extra.txt")

    cards = []
    for L in string.ascii_lowercase:
        f = review / f"{L}.txt"
        words = [w for w in cand if w[0] == L]
        if not f.exists():
            continue
        keep, remove, hints = parse(f)
        hints = {**hints, **{k: v for k, v in extra_hints.items() if k[0] == L}}
        kept = [w for w in words if (w in keep if keep is not None else w not in remove)]
        for w in kept:
            if w in extra_remove:
                continue
            prompt = hints.get(w) or (("an " if w[0] in "aeiou" else "a ") + w)
            scene = prompt.startswith("!")
            cards.append({
                "word": w, "ipa": ipa(w, cand[w]["phonetic"]), "zh": zh[w], "kind": cand[w]["kind"],
                "rank": cand[w]["rank"], "scene": "y" if scene else "", "prompt": prompt.lstrip("!"),
            })

    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(cards[0]), delimiter="\t")
        w.writeheader()
        w.writerows(cards)
    print("cards:", len(cards), "->", args.out)


if __name__ == "__main__":
    main()
