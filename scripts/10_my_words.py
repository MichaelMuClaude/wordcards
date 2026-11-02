"""Cards for words you looked up yourself: one word or phrase at a time, shown more often in GlanceCards.

    python scripts/10_my_words.py words.tsv ecdict.csv cards_dir --learning ~/word-images/learning [--known ...]

`words.tsv` has the columns word, zh, prompt, ipa (ipa may be empty; `!` before the prompt = a scene
instead of a studio picture). For each word that has no card yet:
- if a card for it is already in the learning or known folder (`apple.png`, `wa_apple.jpg`), it is moved
  to `learning/mine_<word>.<ext>` instead of drawing a new one;
- otherwise a picture is drawn with the local ComfyUI server (resting `--pause` seconds after each), labelled
  with the word, its phonetics (from ECDICT, or the ipa column) and the Chinese, saved in cards_dir and copied
  to `learning/mine_<word>.png`.
GlanceCards puts `mine_` cards, like `sentence_` cards, after every few ordinary cards.

When the cards live on another machine (a `glancecards --serve` server), give the folders scp-style, as
`--learning user@host:path/learning`: the script then looks, moves and copies there over ssh.
"""

import argparse
import csv
import importlib.util
import json
import shlex
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ipa import ipa  # noqa: E402

spec = importlib.util.spec_from_file_location("label", HERE / "04_label.py")
label = importlib.util.module_from_spec(spec)
spec.loader.exec_module(label)

WORKFLOW = HERE.parent / "workflow" / "z_image_turbo_api.json"
STUDIO = ", centered, clean plain light-grey studio background, soft natural light, sharp focus, realistic photo, no text, no watermark"
SCENE = ", soft natural light, sharp focus, realistic photo, no text, no watermark"


def draw(url, prompt, seed, dest):
    g = json.loads(WORKFLOW.read_text(encoding="utf-8"))
    g["4"]["inputs"]["text"] = prompt
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


class Folder:
    """A card folder, here or on another machine (`user@host:path`, reached with ssh and scp)."""

    def __init__(self, spec):
        host, sep, path = spec.partition(":")
        # "C:\..." is a Windows path, not a host.
        self.host, self.path = (host, path) if sep and len(host) > 1 else (None, Path(spec).expanduser())
        self._names = None

    def sibling(self, name):
        parent = str(Path(self.path).parent / name)
        return Folder(f"{self.host}:{parent}" if self.host else parent)

    def names(self):
        if self._names is None:
            if self.host:
                out = subprocess.run(["ssh", self.host, f"ls -1 {shlex.quote(str(self.path))}"], capture_output=True, text=True, check=True)
                self._names = set(out.stdout.splitlines())
            else:
                self._names = {p.name for p in self.path.iterdir()} if self.path.is_dir() else set()
        return self._names

    def has(self, name):
        return name in self.names()

    def move_to(self, name, other, new_name):
        """Moves a card from this folder to `other` (on the same machine) as `new_name`."""
        src, dest = Path(self.path) / name, Path(other.path) / new_name
        if self.host:
            subprocess.run(["ssh", self.host, f"mv -n {shlex.quote(str(src))} {shlex.quote(str(dest))}"], check=True)
        else:
            shutil.move(src, dest)
        self.names().discard(name)
        other.names().add(new_name)

    def put(self, local_file):
        if self.host:
            # No shell quoting here: newer scp sends the path over SFTP as it is.
            subprocess.run(["scp", "-q", str(local_file), f"{self.host}:{self.path}/"], check=True)
        else:
            shutil.copy(local_file, self.path / local_file.name)
        self.names().add(local_file.name)

    def __str__(self):
        return f"{self.host}:{self.path}" if self.host else str(self.path)


def phonetics(word, given, ecdict):
    """The ipa column if filled, else ECDICT's entry, else each word of a phrase looked up on its own."""
    if given.strip():
        return given.strip()
    if word in ecdict and ecdict[word]:
        return ipa(word, ecdict[word])
    parts = [ipa(w, ecdict[w]).strip("/") for w in word.split() if ecdict.get(w)]
    return f"/{' '.join(parts)}/" if parts and len(parts) == len(word.split()) else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("words_tsv")
    ap.add_argument("ecdict_csv")
    ap.add_argument("cards_dir")
    ap.add_argument("--learning", required=True, help="the folder GlanceCards shows (or user@host:path)")
    ap.add_argument("--known", help="GlanceCards' known folder (default: known next to learning)")
    ap.add_argument("--url", default="http://127.0.0.1:8188", help="ComfyUI server")
    ap.add_argument("--seed", type=int, default=40000)
    ap.add_argument("--pause", type=float, default=30, help="seconds to rest after every picture")
    args = ap.parse_args()

    learning = Folder(args.learning)
    known = Folder(args.known) if args.known else learning.sibling("known")
    cards = Path(args.cards_dir)
    raw = cards / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(args.words_tsv, encoding="utf-8"), delimiter="\t"))
    ecdict = None
    for i, r in enumerate(rows):
        word = r["word"].strip()
        slug = word.replace(" ", "-")
        if any(d.has(f"mine_{slug}{ext}") for d in (learning, known) for ext in (".png", ".jpg")):
            continue
        existing = [(d, n) for d in (learning, known) for n in (f"{word}.png", f"wa_{slug}.jpg") if d.has(n)]
        if existing:
            d, n = existing[0]
            dest = f"mine_{slug}{Path(n).suffix}"
            d.move_to(n, learning, dest)
            print(f"{word}: moved the existing card {d}/{n} to {dest}", flush=True)
            continue
        if ecdict is None:
            ecdict = {e["word"]: e["phonetic"] for e in csv.DictReader(open(args.ecdict_csv, encoding="utf-8", newline=""))}
        pic = raw / f"{slug}.png"
        if not pic.exists():
            prompt = r["prompt"].strip()
            full = prompt.lstrip("!") + (SCENE if prompt.startswith("!") else STUDIO)
            draw(args.url, full, args.seed + i, pic)
            print(f"{word}: drew a picture, resting {args.pause:.0f}s", flush=True)
            time.sleep(args.pause)
        card = cards / f"mine_{slug}.png"
        label.label_card(Image.open(pic), word, phonetics(word, r.get("ipa") or "", ecdict), r["zh"]).save(card)
        learning.put(card)
        print(f"{word}: card {card.name} copied to {learning}", flush=True)


if __name__ == "__main__":
    main()
