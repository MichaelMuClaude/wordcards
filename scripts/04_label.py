"""Step 4: put the word, its phonetics and its Chinese meaning under each picture.

    python scripts/04_label.py data/cards.tsv raw/ cards/

Needs Pillow, the DejaVu Sans fonts and Noto Sans CJK (paths below; change them for your system).
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
        img = Image.open(src).convert("RGB")
        w, h = img.size
        canvas = Image.new("RGB", (w, h + BAND), (250, 247, 240))
        canvas.paste(img, (0, 0))
        d = ImageDraw.Draw(canvas)
        size = 120
        while size > 60:
            fw = ImageFont.truetype(BOLD, size)
            if d.textlength(word, font=fw) <= w - 80:
                break
            size -= 6
        lines = [(word, fw, (30, 30, 30), 20)]
        if r["ipa"]:
            fp = ImageFont.truetype(REG, 58)
            while d.textlength(r["ipa"], font=fp) > w - 80:
                fp = ImageFont.truetype(REG, fp.size - 4)
            lines.append((r["ipa"], fp, (110, 110, 110), 20))
        lines.append((r["zh"], ImageFont.truetype(CJK, 72, index=CJK_INDEX), (160, 60, 40), 0))
        y = h + 24
        for text, font, color, gap in lines:
            box = d.textbbox((0, 0), text, font=font)
            d.text(((w - (box[2] - box[0])) / 2 - box[0], y - box[1]), text, font=font, fill=color)
            y += box[3] - box[1] + gap + 14
        canvas.save(out / f"{word}.png")
        made += 1
    print("labeled", made)


if __name__ == "__main__":
    main()
