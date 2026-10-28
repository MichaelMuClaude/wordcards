# wordcards

771 picture cards for everyday English nouns, and the pipeline that made them.

Each card is a picture of one thing (apple, ladder, hummingbird, stove ...) with the word, its
phonetics and its Chinese meaning underneath. The pictures are AI-generated, the word list was
picked from a dictionary by script and then reviewed by hand, and everything here is open so you can
rebuild it, change it or make your own set.

![Some cards](docs/overview.jpg)

Made to be shown one after another on the desktop by [wordnote](https://github.com/MichaelMuClaude/wordnote),
a small sticky-note app: you glance at the cards while you work, and click **Got it** on the ones you
already know.

## 中文简介

771 张日常英语名词的图片卡片：一张图配上单词、音标和中文释义。图片由 AI 生成，词表先用脚本从
ECDICT 词典里筛选，再人工逐个审过（只留生活里看得见、画得出来的东西）。整套流程（选词、出图、加字）
都在这个仓库里，可以自己重做或换成别的词表。配合桌面便签小程序
[wordnote](https://github.com/MichaelMuClaude/wordnote) 使用：干活时随手瞄几眼，认识的点 **Got it** 就不再出现。

## Download

The pictures are too big for the repository, so they are attached to the
[Releases](https://github.com/MichaelMuClaude/wordcards/releases) page:

| File | What is in it | Size |
|---|---|---|
| `wordcards-v1-cards.zip` | 771 finished cards (picture + word + phonetics + Chinese), 1024x1404 JPEG | about 107 MB |
| `wordcards-v1-pictures-only.zip` | the same 771 pictures without any text, 1024x1024 JPEG | about 92 MB |

## What is in this repository

| Path | Content |
|---|---|
| `data/cards.tsv` | the final list: word, IPA, Chinese meaning, category, ECDICT frequency rank, and the prompt used to draw it |
| `data/zh.json` | the Chinese meanings (short everyday wording, written by hand rather than copied from the dictionary) |
| `data/candidates_rank20000.tsv` | 2988 concrete-noun candidates picked from the dictionary before the manual review |
| `data/review/` | the manual review, one file per letter: which words to keep, and how to draw the ambiguous ones |
| `scripts/` | the four pipeline steps below |
| `workflow/z_image_turbo_api.json` | the ComfyUI graph used for every picture (API format) |

## How the cards were made

1. **Pick candidates** (`scripts/01_screen_nouns.py`). Take the 20000 most frequent entries of
   [ECDICT](https://github.com/skywind3000/ECDICT) that are single-word nouns, and keep those whose
   first [WordNet](https://wordnet.princeton.edu/) sense is something concrete (animal, artifact, food,
   body, plant, natural object, substance, weather). That gives 2988 words, including many that are not
   really drawable (`bank` as a river bank, `blackjack`, `bender` ...).
2. **Review by hand** (`data/review/*.txt`, `scripts/02_build_cards.py`). Keep only everyday things you can
   point at and draw: no abstract, scientific, medical, military or obscure words. For every word that
   has more than one common meaning, write the picture description (`bat` = a bat hanging upside down,
   `bulb` = a light bulb). 771 words remain.
3. **Draw** (`scripts/03_generate.py`). One 1024x1024 picture per word with a local
   [ComfyUI](https://github.com/comfyanonymous/ComfyUI) server running Z-Image-Turbo (9 steps, about 3
   seconds per picture on an RTX 5090). Objects get a plain light-grey studio background; scenes
   (landscapes, rooms, buildings) get natural light instead.
4. **Label** (`scripts/04_label.py`). Pillow adds a strip with the word, IPA and Chinese meaning.

The first pass left about a third of the pictures weak or wrong (an empty room for `attic`, a button for
`mushroom`, a pencil for `crayon`). The prompts for those were rewritten and the pictures redrawn; the
rewritten prompts are the ones in `data/review/extra.txt`.

## Rebuild it yourself

```bash
pip install -r requirements.txt
python -c "import nltk; nltk.download('wordnet')"

# 1. candidates (download ecdict.csv from the ECDICT repository first)
python scripts/01_screen_nouns.py ecdict.csv data/candidates_rank20000.tsv

# 2. apply the review -> data/cards.tsv
python scripts/02_build_cards.py

# 3. draw (ComfyUI running with z_image_turbo_bf16, qwen_3_4b and z_image_ae installed)
python scripts/03_generate.py data/cards.tsv raw/

# 4. add the text strip
python scripts/04_label.py data/cards.tsv raw/ cards/
```

Step 4 expects DejaVu Sans and Noto Sans CJK at the paths at the top of `scripts/04_label.py`.

## Things to know

- **The pictures are not perfect.** Some have stray text the model drew by itself (a shop sign, the
  writing on a toothpaste tube), some are a bit small in the frame, and a few words are shown by one
  of several possible things (`mouse` is the animal, not the computer mouse). I checked every picture
  as a thumbnail, not at full size.
- **Seeds.** The published set was drawn in several batches, so re-running step 3 gives similar but not
  identical pictures.
- **Phonetics** come from ECDICT, converted to standard IPA symbols (11 broken entries were fixed by
  hand in `scripts/ipa.py`). They follow British-style notation.
- **Chinese meanings** were written with the help of an AI model and have not been proofread by a
  professional; corrections are welcome.
- The cards are all in one realistic-photo style. To get a different look, change the prompt suffixes in
  `scripts/03_generate.py` and redraw.

## License and credits

- Code in this repository: MIT, see [LICENSE](LICENSE).
- The picture cards, `data/cards.tsv`, `data/zh.json` and the review files: CC BY 4.0
  (credit "wordcards by Michael Mu"). The pictures are AI-generated, and how copyright applies to
  such images differs between countries.
- The word list, phonetics and frequency ranks are derived from ECDICT (MIT) and the category filter
  uses WordNet. Full credits and the licenses of the tools and models used are in [NOTICE.md](NOTICE.md).
