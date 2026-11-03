"""Build data/set8/cards.tsv (50 car and driving words) from the hand-written specs.

    python scripts/13_build_set8.py path/to/ecdict.csv

Same layout as set 7 (scripts/12_build_set7.py): each line of data/set8/specs/spec_car.txt is
`word|Chinese meaning|prompt`, a leading `!` on the prompt means a scene-style picture, and
data/set8/fixes.txt (optional) holds prompts rewritten after the first drawing round. Unlike sets 6 and 7 this
set is a theme, not the next stretch of the ECDICT list: parts of a car, kinds of car and things on the road,
with Australian names (tyre, number plate, give way sign, L plates). Many are two-word names that ECDICT lacks,
so their phonetics are in scripts/ipa.py and the rank is left empty. Files are named with spaces turned into
hyphens (`steering-wheel.png`).
"""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ipa import ipa  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SET8 = ROOT / "data" / "set8"
KINDS = [("car", "thing")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ecdict_csv")
    ap.add_argument("--out", default=SET8 / "cards.tsv")
    args = ap.parse_args()

    ecdict = {r["word"]: r for r in csv.DictReader(open(args.ecdict_csv, encoding="utf-8", newline=""))}
    fixes = {}
    fixes_file = SET8 / "fixes.txt"
    if fixes_file.exists():
        for line in fixes_file.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                k, v = line.split("=", 1)
                fixes[k] = v

    rows = []
    for name, kind in KINDS:
        for line in (SET8 / "specs" / f"spec_{name}.txt").read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            word, zh, prompt = line.split("|", 2)
            prompt = fixes.get(word, prompt)
            rows.append({
                "word": word, "ipa": ipa(word, ecdict[word]["phonetic"] if word in ecdict else ""), "zh": zh, "kind": kind,
                "rank": ecdict[word]["frq"] if word in ecdict else "", "scene": "y" if prompt.startswith("!") else "", "prompt": prompt.lstrip("!"),
            })

    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    print("set 8 cards:", len(rows), "->", args.out)


if __name__ == "__main__":
    main()
