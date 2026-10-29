"""Step 3: make one picture per word with a local ComfyUI server (Z-Image-Turbo, 1024x1024, 9 steps).

    python scripts/03_generate.py data/cards.tsv raw/ [--only apple,pear] [--url http://127.0.0.1:8188]

Words whose PNG already exists in the output folder are skipped, so a stopped run can be resumed.
Seeds are base-seed + position in the cards file, so a re-run gives similar but not identical pictures
to the published set (it was made in several batches).
"""

import argparse
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

STUDIO = ", centered, clean plain light-grey studio background, soft natural light, sharp focus, realistic photo, no text, no watermark"
SCENE = ", soft natural light, sharp focus, realistic photo, no text, no watermark"
NEG = "text, letters, watermark, logo, blurry, multiple objects, cluttered background"
SCENE_WORDS = (" in a ", " in snow", " on a ", " over ", " at ", " on grass", " by ", " in the ", " with a ", "interior", "exterior", "building", "street", "sky")

WORKFLOW = Path(__file__).resolve().parent.parent / "workflow" / "z_image_turbo_api.json"


def build_graph(positive, negative, seed):
    g = json.loads(WORKFLOW.read_text(encoding="utf-8"))
    g["4"]["inputs"]["text"] = positive
    g["5"]["inputs"]["text"] = negative
    g["7"]["inputs"]["seed"] = seed
    return g


def post(url, path, obj):
    req = urllib.request.Request(url + path, data=json.dumps(obj).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cards_tsv")
    ap.add_argument("out_dir")
    ap.add_argument("--url", default="http://127.0.0.1:8188", help="ComfyUI server")
    ap.add_argument("--only", default="", help="comma-separated words (default: all)")
    ap.add_argument("--seed", type=int, default=5000)
    ap.add_argument("--pause", type=float, default=0, help="seconds to rest after every picture")
    ap.add_argument("--rest-every", type=int, default=0, help="take a long rest after this many pictures (0 = never)")
    ap.add_argument("--rest", type=float, default=60, help="seconds of the long rest")
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    only = {w for w in args.only.split(",") if w}
    rows = list(csv.DictReader(open(args.cards_tsv, encoding="utf-8"), delimiter="\t"))
    made = 0
    for i, r in enumerate(rows):
        word, prompt = r["word"], r["prompt"]
        dest = out / f"{word}.png"
        if (only and word not in only) or dest.exists():
            continue
        scene = r.get("scene") == "y" or r["kind"] in ("nature", "phenomenon") or any(s in prompt for s in SCENE_WORDS)
        pid = post(args.url, "/prompt", {"prompt": build_graph(prompt + (SCENE if scene else STUDIO), NEG, args.seed + i)})["prompt_id"]
        t0 = time.time()
        while True:
            h = json.loads(urllib.request.urlopen(f"{args.url}/history/{pid}", timeout=15).read())
            if pid in h and h[pid].get("outputs"):
                img = h[pid]["outputs"]["9"]["images"][0]
                break
            if time.time() - t0 > 300:
                sys.exit(f"timeout on {word}")
            time.sleep(0.5)
        q = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img["subfolder"], "type": img["type"]})
        dest.write_bytes(urllib.request.urlopen(f"{args.url}/view?{q}", timeout=60).read())
        print(f"{i + 1}/{len(rows)} {word} {'scene' if scene else 'studio'} {time.time() - t0:.1f}s", flush=True)
        made += 1
        time.sleep(args.pause)
        if args.rest_every and made % args.rest_every == 0:
            time.sleep(args.rest)
    print("done")


if __name__ == "__main__":
    main()
