"""Build data/set4/cards.tsv (the fourth set of 500 cards) from the hand-written specs.

    python scripts/07_build_set4.py path/to/ecdict.csv

Same idea as set 2 (scripts/05_build_set2.py): each line of data/set4/specs/spec_*.txt is
`word|Chinese meaning|prompt`, a leading `!` on the prompt means a scene-style picture, and
data/set4/fixes.txt (optional) holds prompts rewritten after the first drawing round. Set 4 adds more animals, food, things around the house, tools, office and tech items, vehicles, places,
nature, clothes, jobs and characters, body and medical words, sports and music, actions and adjectives.
ECDICT supplies the phonetics and frequency rank.
"""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ipa import ipa  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SET4 = ROOT / "data" / "set4"
KINDS = [("animals", "thing"), ("food", "thing"), ("home", "thing"), ("tools", "thing"), ("office", "thing"),
         ("transport", "thing"), ("places", "thing"), ("nature", "thing"), ("clothes", "thing"), ("body", "thing"),
         ("sports", "thing"), ("people", "person"), ("verbs", "action"), ("adj", "adjective")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ecdict_csv")
    ap.add_argument("--out", default=SET4 / "cards.tsv")
    args = ap.parse_args()

    ecdict = {r["word"]: r for r in csv.DictReader(open(args.ecdict_csv, encoding="utf-8", newline=""))}
    fixes = {}
    fixes_file = SET4 / "fixes.txt"
    if fixes_file.exists():
        for line in fixes_file.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                k, v = line.split("=", 1)
                fixes[k] = v

    rows = []
    for name, kind in KINDS:
        for line in (SET4 / "specs" / f"spec_{name}.txt").read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            word, zh, prompt = line.split("|", 2)
            prompt = fixes.get(word, prompt)
            rows.append({
                "word": word, "ipa": ipa(word, ecdict[word]["phonetic"]), "zh": zh, "kind": kind,
                "rank": ecdict[word]["frq"], "scene": "y" if prompt.startswith("!") else "", "prompt": prompt.lstrip("!"),
            })

    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    print("set 4 cards:", len(rows), "->", args.out)


if __name__ == "__main__":
    main()
