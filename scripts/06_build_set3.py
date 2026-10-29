"""Build data/set3/cards.tsv (the third set of 500 cards) from the hand-written specs.

    python scripts/06_build_set3.py path/to/ecdict.csv

Same idea as set 2 (scripts/05_build_set2.py): each line of data/set3/specs/spec_*.txt is
`word|Chinese meaning|prompt`, a leading `!` on the prompt means a scene-style picture, and
data/set3/fixes.txt (optional) holds prompts rewritten after the first drawing round. Set 3 adds more
animals, nature, things around the house, clothes, food, places and vehicles, tools, sports and toys,
body parts, jobs, feelings, actions and adjectives. ECDICT supplies the phonetics and frequency rank.
"""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ipa import ipa  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SET3 = ROOT / "data" / "set3"
KINDS = [("animals", "thing"), ("nature", "thing"), ("home", "thing"), ("clothes", "thing"), ("food", "thing"),
         ("places", "thing"), ("things", "thing"), ("body", "thing"), ("people", "person"),
         ("verbs", "action"), ("adj", "adjective")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ecdict_csv")
    ap.add_argument("--out", default=SET3 / "cards.tsv")
    args = ap.parse_args()

    ecdict = {r["word"]: r for r in csv.DictReader(open(args.ecdict_csv, encoding="utf-8", newline=""))}
    fixes = {}
    fixes_file = SET3 / "fixes.txt"
    if fixes_file.exists():
        for line in fixes_file.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                k, v = line.split("=", 1)
                fixes[k] = v

    rows = []
    for name, kind in KINDS:
        for line in (SET3 / "specs" / f"spec_{name}.txt").read_text(encoding="utf-8").splitlines():
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
    print("set 3 cards:", len(rows), "->", args.out)


if __name__ == "__main__":
    main()
