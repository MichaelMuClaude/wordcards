"""Step 1: pick concrete-noun candidates from ECDICT using WordNet's first-sense category.

    python scripts/01_screen_nouns.py ecdict.csv data/candidates_rank20000.tsv --max-rank 20000

Needs `pip install nltk` and `python -c "import nltk; nltk.download('wordnet')"`.
"""

import argparse
import csv
import re
from collections import Counter

from nltk.corpus import wordnet as wn

# WordNet first-sense categories that are usually something you can point at and draw.
CONCRETE = {
    "noun.animal": "animal", "noun.artifact": "thing", "noun.food": "food", "noun.body": "body",
    "noun.plant": "plant", "noun.object": "nature", "noun.substance": "material",
    "noun.phenomenon": "phenomenon",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ecdict_csv")
    ap.add_argument("out_tsv")
    ap.add_argument("--max-rank", type=int, default=20000, help="ECDICT frq rank cut-off")
    args = ap.parse_args()

    rows = []
    with open(args.ecdict_csv, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            w = r["word"]
            if not re.fullmatch(r"[a-z]{3,}", w):
                continue
            frq = int(r["frq"] or 0)
            if not 0 < frq <= args.max_rank:
                continue
            first = (r["translation"] or "").split("\n")[0]
            if not first.startswith("n."):
                continue
            syn = wn.synsets(w, pos="n")
            if not syn or wn.morphy(w, "n") != w:  # skip plurals / inflected forms
                continue
            lex = syn[0].lexname()
            if lex not in CONCRETE:
                continue
            others = {s.lexname() for s in syn[1:3]} - {lex}  # other top senses in a different category
            rows.append({
                "word": w, "rank": frq, "kind": CONCRETE[lex], "ambig": "y" if others else "",
                "phonetic": r["phonetic"],
                "zh": first[3:].split("\\n")[0].split(";")[0].split(",")[0].strip()[:20],
                "gloss": syn[0].definition()[:70],
            })

    rows.sort(key=lambda x: x["word"])
    with open(args.out_tsv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    print("candidates:", len(rows), dict(Counter(r["kind"] for r in rows)))


if __name__ == "__main__":
    main()
