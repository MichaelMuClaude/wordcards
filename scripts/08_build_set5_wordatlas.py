"""Build set 5 from the Word Atlas dataset (https://github.com/designfuchen/word-atlas, CC BY 4.0).

    python scripts/08_build_set5_wordatlas.py path/to/word-atlas cards5/

Reads data/word-atlas.json and public/atlas/img/*.webp from a clone of that repository, writes
data/set5/cards.tsv (word, IPA, Chinese meaning, topic, CEFR level, Word Atlas id) and one finished card per
word, `wa_<id>.jpg`, in the output folder. The card is the original 512 px illustration with a strip under
it (the same layout as the other sets, scaled down). The `wa_` prefix keeps the files apart from sets 1 to 4,
because some words are in both. We only reformat: the words, IPA (British), the first Chinese meaning and
the pictures are Word Atlas's, credited in NOTICE.md.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from importlib import import_module  # noqa: E402

label_card = import_module("04_label").label_card

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ["word", "ipa", "zh", "topic", "cefr", "id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("word_atlas_dir", help="a clone of designfuchen/word-atlas")
    ap.add_argument("out_dir", help="where the finished cards go")
    ap.add_argument("--tsv", default=ROOT / "data" / "set5" / "cards.tsv")
    args = ap.parse_args()

    src = Path(args.word_atlas_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    Path(args.tsv).parent.mkdir(parents=True, exist_ok=True)
    entries = json.loads((src / "data" / "word-atlas.json").read_text(encoding="utf-8"))

    rows, made = [], 0
    for e in entries:
        img = src / "public" / "atlas" / "img" / f"{e['id']}.webp"
        if not img.exists() or not e.get("senses"):
            print("skipped (no picture or meaning):", e["id"])
            continue
        row = {"word": e["w"], "ipa": e.get("uk", ""), "zh": e["senses"][0]["zh"], "topic": e["topic"],
               "cefr": e["cefr"], "id": e["id"]}
        dest = out / f"wa_{e['id']}.jpg"
        if not dest.exists():
            label_card(Image.open(img), row["word"], row["ipa"], row["zh"]).save(dest, quality=90)
            made += 1
        rows.append(row)

    with open(args.tsv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    print(f"set 5 cards: {len(rows)} ({made} drawn now) -> {args.tsv}")


if __name__ == "__main__":
    main()
