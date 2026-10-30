# wordcards

9569 picture cards for everyday English words, and the pipeline that made them.

Each card is a picture with the word, its phonetics and its Chinese meaning underneath. The pictures
are AI-generated. Set 1 (771 cards) is everyday nouns picked from a dictionary by script and then
reviewed by hand; set 2 (500 cards) was written by hand and adds the basics that set 1 missed: more
nouns, jobs and people, actions, adjectives, colours and shapes, seasons and position words; set 3
(500 cards, also by hand) goes further: more animals, nature, food, clothes, places and vehicles, tools,
body parts, feelings, actions and adjectives. Set 4 (500 cards, by hand again) adds world foods, tools, tech, vehicles, gems and plants,
fantasy characters, sports and instruments. Set 5 (7298 cards) is not ours: it is the illustrated
vocabulary of [Word Atlas](https://github.com/designfuchen/word-atlas) (CC BY 4.0), reformatted as cards in the same
layout, in a different (flat illustration) style. Everything here is open so you can rebuild it, change it or make your own set.

![Some cards from set 1](docs/overview.jpg)

![Some cards from set 2](docs/overview2.jpg)

![Some cards from set 3](docs/overview3.jpg)

![Some cards from set 4](docs/overview4.jpg)

![Some cards from set 5 (Word Atlas)](docs/overview5.jpg)

Made to be shown one after another on the desktop by [GlanceCards](https://github.com/MichaelMuClaude/glancecards),
a small desktop card window: you glance at the cards while you work, and click **Got it** on the ones you
already know.

## 中文简介

共 9569 张日常英语卡片：一张图配上单词、音标和中文释义，图片由 AI 生成。
第一组 771 张是日常名词，先用脚本从 ECDICT 词典里筛选，再人工逐个审过（只留生活里看得见、画得出来的东西）；
第二组 500 张是手写的名单，补上第一组漏掉的基础词：更多名词、职业和人物、动作、形容词、颜色和形状、季节和方位词；
第三组 500 张同样手写，继续补：更多动物、自然景物、食物、衣服、场所和交通工具、工具、身体部位、情绪、动作和形容词；
第四组 500 张继续手写：世界美食、工具、科技、交通工具、宝石和花木、幻想角色、运动和乐器。
第五组 7298 张不是我们画的，来自开源项目 [Word Atlas（词光）](https://github.com/designfuchen/word-atlas)（CC BY 4.0）：
我们只把它的插画和词条按同样的版式做成卡片，风格是扁平插画，很多是场景加抽象词。
整套流程（选词、出图、加字）都在这个仓库里，可以自己重做或换成别的词表。配合桌面小窗口程序
[GlanceCards](https://github.com/MichaelMuClaude/glancecards) 使用：干活时随手瞄几眼，认识的点 **Got it** 就不再出现。

## Download

The pictures are too big for the repository, so they are attached to the
[Releases](https://github.com/MichaelMuClaude/wordcards/releases) page:

| File | What is in it | Size |
|---|---|---|
| `wordcards-v1-cards.zip` (v1.0.0) | set 1: 771 finished cards (picture + word + phonetics + Chinese), 1024x1404 JPEG | about 107 MB |
| `wordcards-v1-pictures-only.zip` (v1.0.0) | set 1: the same 771 pictures without text, 1024x1024 JPEG | about 92 MB |
| `wordcards-v1.1-set2-cards.zip` (v1.1.0) | set 2: 500 finished cards | about 76 MB |
| `wordcards-v1.1-set2-pictures-only.zip` (v1.1.0) | set 2: the same 500 pictures without text | about 67 MB |
| `wordcards-v1.2-set3-cards.zip` (v1.2.0) | set 3: 500 finished cards | about 83 MB |
| `wordcards-v1.2-set3-pictures-only.zip` (v1.2.0) | set 3: the same 500 pictures without text | about 74 MB |
| `wordcards-v1.3-set4-cards.zip` (v1.3.0) | set 4: 500 finished cards | about 81 MB |
| `wordcards-v1.3-set4-pictures-only.zip` (v1.3.0) | set 4: the same 500 pictures without text | about 71 MB |
| `wordcards-v1.4-set5-wordatlas-cards.zip` (v1.4.0) | set 5: 7298 cards from Word Atlas, 512x702 JPEG, files named `wa_<id>.jpg` | about 570 MB |

Sets 1 to 4 have no words in common, so you can unzip them into one folder. Set 5 shares 1275 words with them (a
different picture each), which is why its files start with `wa_`; they can go into the same folder too.

## What is in this repository

| Path | Content |
|---|---|
| `data/cards.tsv` | set 1: word, IPA, Chinese meaning, category, ECDICT frequency rank, and the prompt used to draw it |
| `data/zh.json` | the Chinese meanings of set 1 (short everyday wording, written by hand rather than copied from the dictionary) |
| `data/candidates_rank20000.tsv` | 2988 concrete-noun candidates picked from the dictionary before the manual review of set 1 |
| `data/review/` | the manual review of set 1, one file per letter: which words to keep, and how to draw the ambiguous ones |
| `data/set2/cards.tsv` | set 2: the same columns as above |
| `data/set2/specs/` | the hand-written set 2 word lists (`word\|Chinese\|prompt`), and `fixes.txt` with the prompts rewritten after the first drawing round |
| `data/set3/cards.tsv` | set 3: the same columns as above |
| `data/set3/specs/` | the hand-written set 3 word lists (`word\|Chinese\|prompt`), and `fixes.txt` with the prompts rewritten after the first drawing round |
| `data/set4/cards.tsv` | set 4: the same columns as above |
| `data/set4/specs/` | the hand-written set 4 word lists (`word\|Chinese\|prompt`), and `fixes.txt` with the prompts rewritten after the first drawing round |
| `data/set5/cards.tsv` | set 5 (Word Atlas): word, British IPA, first Chinese meaning, topic, CEFR level, Word Atlas id |
| `scripts/` | the pipeline steps below |
| `workflow/z_image_turbo_api.json` | the ComfyUI graph used for every picture (API format) |

## How the cards were made

**Set 1**

1. **Pick candidates** (`scripts/01_screen_nouns.py`). Take the 20000 most frequent entries of
   [ECDICT](https://github.com/skywind3000/ECDICT) that are single-word nouns, and keep those whose
   first [WordNet](https://wordnet.princeton.edu/) sense is something concrete (animal, artifact, food,
   body, plant, natural object, substance, weather). That gives 2988 words, including many that are not
   really drawable (`bank` as a river bank, `blackjack`, `bender` ...).
2. **Review by hand** (`data/review/*.txt`, `scripts/02_build_cards.py`). Keep only everyday things you can
   point at and draw: no abstract, scientific, medical, military or obscure words. For every word that
   has more than one common meaning, write the picture description (`bat` = a bat hanging upside down,
   `bulb` = a light bulb). 771 words remain.

**Set 2**

The filter above cannot find words like `table` or `book` (WordNet's first sense for them is abstract) and
has no jobs, actions or adjectives. So set 2 is a hand-written list, checked against ECDICT for
phonetics: `data/set2/specs/`, built by `scripts/05_build_set2.py`. Actions are drawn as a person doing
them (`hug` = two friends hugging), adjectives with a typical scene (`big` = an elephant next to a tiny
person), colours with a still life of things of that colour. Four words were left out because set 1
already has the same word as a different thing: the colour `orange`, and the actions `fly`, `paint`
and `slide`.

**Set 3**

Same method as set 2 (`data/set3/specs/`, built by `scripts/06_build_set3.py`), with a new list of 500
words that appear in neither earlier set: animals (yak, toucan, sloth), nature (geyser, reef, oasis),
food, clothes, places and vehicles, tools, body parts, jobs, feelings, actions and adjectives. The list
was checked against ECDICT for phonetics and against sets 1 and 2 for duplicates (five clashes were cut).
Set 3 also dropped `hoe`: the model drew a shovel every time, so it was replaced by `anvil`.

**Set 4**

Same method again (`data/set4/specs/`, built by `scripts/07_build_set4.py`), with another 500 words that
appear in none of the earlier sets: more animals, world foods and spices, things around the house, tools,
office and tech items, vehicles, places, gems, trees and flowers, sky and weather, clothes, jobs and
fantasy characters, body and medical words, sports and instruments, actions and adjectives. About 90 more
candidates were cut while writing the list (duplicates of earlier sets, words ECDICT lacks, and words
that would not draw well). `bassoon` was replaced by `cowbell` because the model drew a clarinet twice.

**Set 5 (from Word Atlas)**

Not made here. [Word Atlas](https://github.com/designfuchen/word-atlas) by designfuchen is an illustrated
IELTS vocabulary of 7298 words with AI-made illustrations (flat mid-century style, 512 px), published under
CC BY 4.0. `scripts/08_build_set5_wordatlas.py` takes a clone of that repository and turns every entry into a
card in our layout: the picture, the word, the British IPA and the first Chinese meaning, written to
`data/set5/cards.tsv` and one `wa_<id>.jpg` per word. The pictures are Word Atlas's own and are not edited. Many of
them show a scene rather than one object, and many of the words are abstract (society, thinking, economy), so
they are harder to read at a glance than sets 1 to 4. The label script was changed to scale to the picture
width (`label_card` in `scripts/04_label.py`); its output for 1024 px pictures is unchanged.

**Sets 1 to 4**

3. **Draw** (`scripts/03_generate.py`). One 1024x1024 picture per word with a local
   [ComfyUI](https://github.com/comfyanonymous/ComfyUI) server running Z-Image-Turbo (9 steps, about 3
   seconds per picture on an RTX 5090). Objects get a plain light-grey studio background; scenes
   (landscapes, rooms, buildings, people doing things) get natural light instead.
4. **Label** (`scripts/04_label.py`). Pillow adds a strip with the word, IPA and Chinese meaning.

In every set the first pass left some pictures weak or wrong (an empty room for `attic`, a button for
`mushroom`, a pencil for `crayon`; in set 2 a human face for `bright` and a single chopstick for
`chopsticks`; in set 3 a bird for `glider` and a table fork for `pitchfork`; in set 4 two separate bikes for
`tandem` and a stepladder for `walker`). The prompts for those were
rewritten and the pictures redrawn: 36 in set 1 (see `data/review/extra.txt`), 10 in set 2
(`data/set2/fixes.txt`) 24 in set 3 (`data/set3/fixes.txt`) and 25 in set 4 (`data/set4/fixes.txt`). `arrow` is shown as a quiver of arrows
because the model kept drawing a feather quill.

## Rebuild it yourself

```bash
pip install -r requirements.txt
python -c "import nltk; nltk.download('wordnet')"

# set 1
python scripts/01_screen_nouns.py ecdict.csv data/candidates_rank20000.tsv   # download ecdict.csv from the ECDICT repository first
python scripts/02_build_cards.py                                             # -> data/cards.tsv

# set 2
python scripts/05_build_set2.py ecdict.csv                                   # -> data/set2/cards.tsv

# set 3
python scripts/06_build_set3.py ecdict.csv                                   # -> data/set3/cards.tsv

# set 4
python scripts/07_build_set4.py ecdict.csv                                   # -> data/set4/cards.tsv

# set 5 (needs a clone of https://github.com/designfuchen/word-atlas)
python scripts/08_build_set5_wordatlas.py ../word-atlas cards5/              # -> data/set5/cards.tsv and cards5/wa_*.jpg

# draw (ComfyUI running with z_image_turbo_bf16, qwen_3_4b and z_image_ae installed), then add the text strip
python scripts/03_generate.py data/cards.tsv raw/
python scripts/04_label.py data/cards.tsv raw/ cards/
python scripts/03_generate.py data/set2/cards.tsv raw2/ --seed 9000
python scripts/04_label.py data/set2/cards.tsv raw2/ cards2/
python scripts/03_generate.py data/set3/cards.tsv raw3/ --seed 12000
python scripts/04_label.py data/set3/cards.tsv raw3/ cards3/
python scripts/03_generate.py data/set4/cards.tsv raw4/ --seed 20000 --pause 3 --rest-every 20
python scripts/04_label.py data/set4/cards.tsv raw4/ cards4/
```

Step 4 expects DejaVu Sans and Noto Sans CJK at the paths at the top of `scripts/04_label.py`.

## Things to know

- **The pictures are not perfect.** Some have stray text the model drew by itself (a shop sign, the
  writing on a toothpaste tube, a made-up brand on a battery), some are a bit small in the frame, and a
  few words are shown by one of several possible things (`mouse` is the animal, not the computer mouse).
  In set 4, `tandem` is only a long bike frame and `arcade` and `gauge` carry a few made-up letters.
  In set 3, for example, `coupon` has a made-up word in the picture, `cork` has some small stray text,
  `scar` is only a mild mark on a knee and `checkers` is drawn as a Chinese-checkers-style board.
  I checked every picture as a thumbnail, not at full size. Actions and adjectives are harder to draw than
  objects, so set 2 has more cases where the picture only roughly fits.
- **Word Atlas is not reviewed by us.** Its author says the texts, pictures and recordings were made with AI and
  not checked entry by entry, and we did not check them either. The Chinese on a set 5 card is the first meaning
  only; many words have more.
- **People.** Sets 2, 3 and 4 have pictures of people. They are AI-generated faces, not real photographs of anyone.
- **Rest the GPU.** Drawing 500 pictures back to back at full load crashed one machine's GPU twice (a hard
  freeze). Set 4 was drawn with `--pause 3 --rest-every 20` (3 s after each picture, 60 s after every 20) and
  finished without a problem. This is one machine's experience, not a general rule.
- **Seeds.** The published sets were drawn in several batches, so re-running step 3 gives similar but not
  identical pictures.
- **Phonetics** come from ECDICT, converted to standard IPA symbols (84 broken or missing entries were fixed by
  hand in `scripts/ipa.py`). They follow British-style notation, and a word-final `i` is written `ɪ`
  (thirsty is `/ˈθɜːstɪ/`), as in ECDICT's own notation.
- **Chinese meanings** were written with the help of an AI model and have not been proofread by a
  professional; corrections are welcome.
- The cards are all in one realistic-photo style. To get a different look, change the prompt suffixes in
  `scripts/03_generate.py` and redraw.

## License and credits

- Code in this repository: MIT, see [LICENSE](LICENSE).
- The picture cards of sets 1 to 4, their `cards.tsv` files, `data/zh.json`, the set 2, 3 and 4 word lists and the review files:
  CC BY 4.0 (credit "wordcards by Michael Mu"). The pictures are AI-generated, and how copyright
  applies to such images differs between countries.
- Set 5 (`data/set5/`, the `wa_*` cards): the words, pictures and meanings are from Word Atlas, CC BY 4.0, "Word Atlas
  contributors"; we only reformatted them (see NOTICE.md).
- The word list, phonetics and frequency ranks are derived from ECDICT (MIT) and the category filter
  uses WordNet. Full credits and the licenses of the tools and models used are in [NOTICE.md](NOTICE.md).
