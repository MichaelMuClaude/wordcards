"""Build data/set11/cards.tsv (100 everyday-life words) from the hand-written specs.

    python scripts/16_build_set11.py path/to/ecdict.csv

Same layout as set 10 (scripts/15_build_set10.py): each line of data/set11/specs/spec_life.txt is
`word|Chinese meaning|prompt`, a leading `!` on the prompt means a scene-style picture, and
data/set11/fixes.txt (optional) holds prompts rewritten after the first drawing round. Set 10 finished the
alphabetical walk through data/candidates_rank20000.tsv; set 11 goes back over the candidates skipped on the way
and picks 100 everyday words that are easy to draw (home, food and drink, animals, plants, weather, body). ECDICT supplies the phonetics and frequency rank.
"""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ipa import ipa  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SET11 = ROOT / "data" / "set11"
KINDS = [("life", "thing")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ecdict_csv")
    ap.add_argument("--out", default=SET11 / "cards.tsv")
    args = ap.parse_args()

    ecdict = {r["word"]: r for r in csv.DictReader(open(args.ecdict_csv, encoding="utf-8", newline=""))}
    fixes = {}
    fixes_file = SET11 / "fixes.txt"
    if fixes_file.exists():
        for line in fixes_file.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                k, v = line.split("=", 1)
                fixes[k] = v

    rows = []
    for name, kind in KINDS:
        for line in (SET11 / "specs" / f"spec_{name}.txt").read_text(encoding="utf-8").splitlines():
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
    print("set 11 cards:", len(rows), "->", args.out)


if __name__ == "__main__":
    main()
