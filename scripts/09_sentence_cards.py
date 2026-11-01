"""Sentence cards: a picture with a whole sentence, its Chinese meaning and its key phrases under it.

    python scripts/09_sentence_cards.py sentences.tsv out/ [--pause 30] [--only 001,004]

`sentences.tsv` has the columns id, sentence, zh, phrases, lookup, prompt:
- sentence: the English sentence; parts in [brackets] are printed in colour (the key phrases);
- phrases: `phrase=中文;phrase=中文`, printed as a small glossary line;
- lookup: what GlanceCards' Look up button searches in the dictionary (it is put in the file name).

Pictures are drawn with the local ComfyUI server like scripts/03_generate.py, one at a time with a rest after
each (`--pause`), and kept in out/raw/ so a re-run only relabels. Cards are written as
`out/sentence_<id>_<lookup>.png`, the same width and height as the word cards (1024 x 1404).
"""

import argparse
import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WORKFLOW = Path(__file__).resolve().parent.parent / "workflow" / "z_image_turbo_api.json"
STYLE = ", soft natural light, sharp focus, realistic photo, no text, no watermark"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CJK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
CJK_INDEX = 2
W, H = 1024, 1404
BG = (250, 247, 240)
INK = (30, 30, 30)
KEY = (200, 85, 35)
ZH = (160, 60, 40)
GREY = (110, 110, 110)


def draw_picture(url, prompt, seed, dest):
    g = json.loads(WORKFLOW.read_text(encoding="utf-8"))
    g["4"]["inputs"]["text"] = prompt + STYLE
    g["5"]["inputs"]["text"] = "text, letters, watermark, logo, blurry"
    g["7"]["inputs"]["seed"] = seed
    req = urllib.request.Request(url + "/prompt", data=json.dumps({"prompt": g}).encode(), headers={"Content-Type": "application/json"})
    pid = json.loads(urllib.request.urlopen(req, timeout=30).read())["prompt_id"]
    t0 = time.time()
    while True:
        h = json.loads(urllib.request.urlopen(f"{url}/history/{pid}", timeout=15).read())
        if pid in h and h[pid].get("outputs"):
            img = h[pid]["outputs"]["9"]["images"][0]
            break
        if time.time() - t0 > 300:
            sys.exit(f"timeout on {dest.name}")
        time.sleep(0.5)
    q = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img["subfolder"], "type": img["type"]})
    dest.write_bytes(urllib.request.urlopen(f"{url}/view?{q}", timeout=60).read())
    return time.time() - t0


def wrap_runs(d, runs, width, space):
    """Break (text, font, colour) runs into lines no wider than `width`.

    A word may be made of pieces from several runs ("out" in colour followed by "." in black); each line is a
    list of (piece, font, colour, x)."""
    words, cur = [], []
    for text, font, color in runs:
        for part in re.split(r"(\s+)", text):
            if not part:
                continue
            if part.isspace():
                if cur:
                    words.append(cur)
                cur = []
            else:
                cur.append((part, font, color))
    if cur:
        words.append(cur)
    lines, line, x = [], [], 0.0
    for word in words:
        wlen = sum(d.textlength(p, font=f) for p, f, _ in word)
        gap = space if line else 0
        if line and x + gap + wlen > width:
            lines.append(line)
            line, x, gap = [], 0.0, 0
        x += gap
        for p, f, c in word:
            line.append((p, f, c, x))
            x += d.textlength(p, font=f)
    if line:
        lines.append(line)
    return lines


def wrap_items(d, items, font, width, sep="    "):
    """Lay out glossary items on lines without breaking an item in two."""
    lines = []
    for item in items:
        if lines and d.textlength(lines[-1] + sep + item, font=font) <= width:
            lines[-1] += sep + item
        else:
            lines.append(item)
    return lines


def wrap_cjk(d, text, font, width):
    lines, cur = [], ""
    for ch in text:
        if cur and d.textlength(cur + ch, font=font) > width:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    return lines + [cur] if cur else lines


def label(img, sentence, zh, phrases):
    margin = 64
    width = W - 2 * margin
    probe = ImageDraw.Draw(Image.new("RGB", (W, 10)))
    for size in range(60, 38, -2):
        reg, bold = ImageFont.truetype(REG, size), ImageFont.truetype(BOLD, size)
        runs = [(t, bold if i % 2 else reg, KEY if i % 2 else INK) for i, t in enumerate(re.split(r"[\[\]]", sentence)) if t]
        en_lines = wrap_runs(probe, runs, width, probe.textlength(" ", font=reg))
        if len(en_lines) <= 3:
            break
    fz = ImageFont.truetype(CJK, 46, index=CJK_INDEX)
    zh_lines = wrap_cjk(probe, zh, fz, width)
    fg = ImageFont.truetype(CJK, 34, index=CJK_INDEX)
    items = [" ".join(p.split("=", 1)) for p in phrases.split(";") if "=" in p]
    gloss_lines = wrap_items(probe, items, fg, width)
    en_h, zh_h, g_h = round(size * 1.35), 64, 48
    band = 40 + len(en_lines) * en_h + 18 + len(zh_lines) * zh_h + 14 + len(gloss_lines) * g_h + 30
    pic_h = H - band
    img = img.convert("RGB").resize((W, W))
    top = (W - pic_h) // 2
    card = Image.new("RGB", (W, H), BG)
    card.paste(img.crop((0, top, W, top + pic_h)), (0, 0))
    d = ImageDraw.Draw(card)
    y = pic_h + 40
    for line in en_lines:
        last = line[-1]
        line_w = last[3] + d.textlength(last[0], font=last[1])
        x0 = (W - line_w) / 2
        for part, font, color, x in line:
            d.text((x0 + x, y), part, font=font, fill=color)
        y += en_h
    y += 18
    for text in zh_lines:
        d.text(((W - d.textlength(text, font=fz)) / 2, y), text, font=fz, fill=ZH)
        y += zh_h
    y += 14
    for text in gloss_lines:
        d.text(((W - d.textlength(text, font=fg)) / 2, y), text, font=fg, fill=GREY)
        y += g_h
    return card


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sentences_tsv")
    ap.add_argument("out_dir")
    ap.add_argument("--url", default="http://127.0.0.1:8188", help="ComfyUI server")
    ap.add_argument("--only", default="", help="comma-separated ids (default: all)")
    ap.add_argument("--seed", type=int, default=30000)
    ap.add_argument("--pause", type=float, default=30, help="seconds to rest after every picture")
    args = ap.parse_args()

    out = Path(args.out_dir)
    raw = out / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    only = {s for s in args.only.split(",") if s}
    rows = list(csv.DictReader(open(args.sentences_tsv, encoding="utf-8"), delimiter="\t"))
    for i, r in enumerate(rows):
        if only and r["id"] not in only:
            continue
        pic = raw / f"{r['id']}.png"
        if not pic.exists():
            secs = draw_picture(args.url, r["prompt"], args.seed + i, pic)
            print(f"drew {r['id']} in {secs:.1f}s, resting {args.pause:.0f}s", flush=True)
            time.sleep(args.pause)
        name = f"sentence_{r['id']}_{r['lookup'].strip().replace(' ', '-')}.png"
        label(Image.open(pic), r["sentence"], r["zh"], r["phrases"]).save(out / name)
        print(f"card {name}", flush=True)


if __name__ == "__main__":
    main()
