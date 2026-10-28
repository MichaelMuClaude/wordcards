"""Build data/set2/cards.tsv (the second set of 500 cards) from the hand-written specs.

    python scripts/05_build_set2.py path/to/ecdict.csv

Set 2 was not filtered from the dictionary like set 1. It was written by hand: everyday nouns that set 1
missed (table, book, school ...), jobs and people, actions, adjectives, colours, shapes, seasons and
position words. Each line of data/set2/specs/spec_*.txt is `word|Chinese meaning|prompt`, where a leading
`!` on the prompt means a scene-style picture. data/set2/fixes.txt holds prompts rewritten after the first
drawing round. ECDICT supplies the phonetics and frequency rank.
"""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ipa import ipa  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SET2 = ROOT / "data" / "set2"
KINDS = [("nouns1", "thing"), ("nouns2", "thing"), ("extra", "thing"), ("people", "person"),
         ("verbs", "action"), ("adj", "adjective"), ("misc", "misc")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ecdict_csv")
    ap.add_argument("--out", default=SET2 / "cards.tsv")
    args = ap.parse_args()

    ecdict = {r["word"]: r for r in csv.DictReader(open(args.ecdict_csv, encoding="utf-8", newline=""))}
    fixes = {}
    for line in (SET2 / "fixes.txt").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            k, v = line.split("=", 1)
            fixes[k] = v

    rows = []
    for name, kind in KINDS:
        for line in (SET2 / "specs" / f"spec_{name}.txt").read_text(encoding="utf-8").splitlines():
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
    print("set 2 cards:", len(rows), "->", args.out)


if __name__ == "__main__":
    main()
