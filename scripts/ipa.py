"""Turn ECDICT's ASCII-ish phonetics into standard IPA symbols for display."""

import re

# ECDICT entries that contain junk characters or two pronunciations: fixed by hand.
OVERRIDE = {
    "arugula": "/əˈruːɡələ/", "baguette": "/bæˈɡet/", "castle": "/ˈkɑːsl/", "curry": "/ˈkʌri/",
    "extinguisher": "/ɪkˈstɪŋɡwɪʃə(r)/", "garage": "/ˈɡærɑːʒ/", "hummingbird": "/ˈhʌmɪŋbɜːd/",
    "omelet": "/ˈɒmlɪt/", "seagull": "/ˈsiːɡʌl/", "suit": "/suːt/", "yogurt": "/ˈjɒɡət/",
}


def ipa(word: str, ecdict_phonetic: str) -> str:
    if word in OVERRIDE:
        return OVERRIDE[word]
    s = ecdict_phonetic.replace(".", "").replace(",", "ˌ").replace("'", "ˈ")
    for a, b in (("єә", "ɛə"), ("є", "ɛ"), ("ә:", "ɜː"), ("ә", "ə"), ("ɒ:", "ɔː"), (":", "ː"),
                 ("əu", "əʊ"), ("ei", "eɪ"), ("ai", "aɪ"), ("au", "aʊ"), ("ɔi", "ɔɪ"), ("iə", "ɪə"), ("uə", "ʊə")):
        s = s.replace(a, b)
    s = re.sub(r"i(?!ː)", "ɪ", s)
    s = re.sub(r"u(?!ː)", "ʊ", s)
    return f"/{s}/" if s else ""
