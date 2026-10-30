# Credits and third-party licenses

wordcards builds on the work of others. Nothing below is redistributed in this repository unless stated.

## Data

- **ECDICT**, by skywind3000, MIT License: https://github.com/skywind3000/ECDICT
  The phonetics and frequency ranks in `data/cards.tsv` and `data/candidates_rank20000.tsv` come from
  ECDICT, and the candidates were chosen from its entries. The ECDICT file itself is not included;
  see its repository for the license text and copyright notice.
- **WordNet 3.0**, Princeton University: https://wordnet.princeton.edu/ (accessed through NLTK).
  Only its category labels were used to pre-select candidates; WordNet data is not included.
  See the WordNet license on that site for its terms.

- **Word Atlas** (词光), by designfuchen and contributors, https://github.com/designfuchen/word-atlas.
  Code is MIT; the word list texts, illustrations and pronunciation recordings are CC BY 4.0, attribution
  "Word Atlas contributors — CC BY 4.0" (https://creativecommons.org/licenses/by/4.0/). Set 5 of this
  repository (`data/set5/cards.tsv` and the `wa_*` cards in the release) is made from it. **Changes made by us:**
  the 512 px illustrations are unchanged, a text strip with the word, its British IPA and its first Chinese
  meaning was added under each one, and the entries were put into a tab-separated table. Word Atlas says its
  content was made with AI and not proofread entry by entry, and is provided as is. Its recordings, interface
  sounds and music are not part of this repository.

## Models and tools used to make the pictures (not distributed here)

- **Z-Image-Turbo** (Tongyi-MAI / Alibaba), which its model card states is under the Apache 2.0 license.
  Please check the official model card for the current terms.
- **Qwen3-4B** text encoder, used inside the Z-Image pipeline (Apache 2.0).
- **ComfyUI** (GPL-3.0), run as a separate local server. `workflow/z_image_turbo_api.json` is only a
  description of the node graph.
- **Pillow** (HPND) for the text strip. Fonts used for the strip: DejaVu Sans (free license) and Noto
  Sans CJK (SIL Open Font License); neither is included.

## What this repository adds

- Code (`scripts/`, `workflow/`): MIT, Copyright (c) 2026 Michael Mu.
- Picture cards of sets 1 to 4, `data/cards.tsv` and the other `cards.tsv` of sets 2 to 4, `data/zh.json`,
  `data/review/`: CC BY 4.0, Copyright (c) 2026 Michael Mu.
  https://creativecommons.org/licenses/by/4.0/
- The Chinese meanings and the manual review were produced with the help of Anthropic's Claude.
