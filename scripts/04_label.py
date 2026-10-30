"""Step 4: put the word, its phonetics and its Chinese meaning under each picture.

    python scripts/04_label.py data/cards.tsv raw/ cards/

Needs Pillow, the DejaVu Sans fonts and Noto Sans CJK (paths below; change them for your system).
`label_card` is also used by scripts/08_build_set5_wordatlas.py; it scales everything to the picture width
(the layout is designed for 1024 px).
"""

import argparse
import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
CJK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
CJK_INDEX = 2  # Simplified Chinese inside the .ttc
BAND = 380


def label_card(img, word, ipa, zh):
    """Return the picture with a strip under it holding the word, IPA and Chinese meaning."""
    img = img.convert("RGB")
    w, h = img.size
    s = w / 1024
    band = round(BAND * s)
    margin = round(80 * s)
    canvas = Image.new("RGB", (w, h + band), (250, 247, 240))
    canvas.paste(img, (0, 0))
    d = ImageDraw.Draw(canvas)
    size = round(120 * s)
    while size > round(60 * s):
        fw = ImageFont.truetype(BOLD, size)
        if d.textlength(word, font=fw) <= w - margin:
            break
        size -= max(1, round(6 * s))
    lines = [(word, fw, (30, 30, 30), round(20 * s))]
    if ipa:
        fp = ImageFont.truetype(REG, round(58 * s))
        while d.textlength(ipa, font=fp) > w - margin:
            fp = ImageFont.truetype(REG, fp.size - max(1, round(4 * s)))
        lines.append((ipa, fp, (110, 110, 110), round(20 * s)))
    fz = ImageFont.truetype(CJK, round(72 * s), index=CJK_INDEX)
    while d.textlength(zh, font=fz) > w - margin and fz.size > round(40 * s):
        fz = ImageFont.truetype(CJK, fz.size - 2, index=CJK_INDEX)
    lines.append((zh, fz, (160, 60, 40), 0))
    y = h + round(24 * s)
    for text, font, color, gap in lines:
        box = d.textbbox((0, 0), text, font=font)
        d.text(((w - (box[2] - box[0])) / 2 - box[0], y - box[1]), text, font=font, fill=color)
        y += box[3] - box[1] + gap + round(14 * s)
    return canvas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cards_tsv")
    ap.add_argument("raw_dir")
    ap.add_argument("out_dir")
    args = ap.parse_args()
    raw, out = Path(args.raw_dir), Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    made = 0
    for r in csv.DictReader(open(args.cards_tsv, encoding="utf-8"), delimiter="\t"):
        word = r["word"]
        src = raw / f"{word}.png"
        if not src.exists():
            print("missing picture:", word)
            continue
        label_card(Image.open(src), word, r["ipa"], r["zh"]).save(out / f"{word}.png")
        made += 1
    print("labeled", made)


if __name__ == "__main__":
    main()
