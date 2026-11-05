"""Turn ECDICT's ASCII-ish phonetics into standard IPA symbols for display."""

import re

# ECDICT entries that contain junk characters or two pronunciations: fixed by hand.
OVERRIDE = {
    "arugula": "/əˈruːɡələ/", "baguette": "/bæˈɡet/", "castle": "/ˈkɑːsl/", "curry": "/ˈkʌri/",
    "extinguisher": "/ɪkˈstɪŋɡwɪʃə(r)/", "garage": "/ˈɡærɑːʒ/", "hummingbird": "/ˈhʌmɪŋbɜːd/",
    "omelet": "/ˈɒmlɪt/", "seagull": "/ˈsiːɡʌl/", "suit": "/suːt/", "yogurt": "/ˈjɒɡət/",
    "laptop": "/ˈlæptɒp/", "hotdog": "/ˈhɒtdɒɡ/", "milkshake": "/ˈmɪlkʃeɪk/", "goggles": "/ˈɡɒɡlz/",
    "guava": "/ˈɡwɑːvə/", "trampoline": "/ˈtræmpəliːn/", "desert": "/ˈdezət/", "plant": "/plɑːnt/",
    "piglet": "/ˈpɪɡlɪt/", "row": "/rəʊ/", "tear": "/tɛə/", "photographer": "/fəˈtɒɡrəfə/", "dance": "/dɑːns/",
    "seahorse": "/ˈsiːhɔːs/", "overalls": "/ˈəʊvərɔːlz/", "suspenders": "/səˈspendəz/", "leggings": "/ˈleɡɪŋz/",
    "fries": "/fraɪz/", "ribs": "/rɪbz/", "bored": "/bɔːd/", "ruins": "/ˈruːɪnz/",
    "grater": "/ˈɡreɪtə/", "flan": "/flæn/", "ranch": "/rɑːntʃ/", "buoy": "/bɔɪ/", "mow": "/məʊ/", "sow": "/səʊ/",
    "corgi": "/ˈkɔːɡɪ/", "bulldog": "/ˈbʊldɒɡ/", "gerbil": "/ˈdʒɜːbɪl/", "narwhal": "/ˈnɑːwəl/", "ravioli": "/ˌrævɪˈəʊlɪ/",
    "tempura": "/ˈtempʊrə/", "gnocchi": "/ˈnjɒkɪ/", "sourdough": "/ˈsaʊədəʊ/", "oregano": "/ɒˈreɡənəʊ/",
    "lagoon": "/ləˈɡuːn/", "coatrack": "/ˈkəʊtræk/", "snowplow": "/ˈsnəʊplaʊ/", "router": "/ˈruːtə/", "dinghy": "/ˈdɪŋɡɪ/",
    "rugby": "/ˈrʌɡbɪ/", "laundromat": "/ˈlɔːndrəmæt/", "grate": "/ɡreɪt/", "bow": "/baʊ/", "sparkler": "/ˈspɑːklə/",
    "cast": "/kɑːst/", "superhero": "/ˈsuːpəhɪərəʊ/", "dollhouse": "/ˈdɒlhaʊs/", "sparkling": "/ˈspɑːklɪŋ/",
    "rainforest": "/ˈreɪnfɒrɪst/", "mongoose": "/ˈmɒŋɡuːs/", "soybean": "/ˈsɔɪbiːn/", "coyote": "/kaɪˈəʊtɪ/",
    "asteroid": "/ˈæstərɔɪd/", "ointment": "/ˈɔɪntmənt/", "embroider": "/ɪmˈbrɔɪdə/", "crouch": "/kraʊtʃ/",
    "wonton": "/ˈwɒntɒn/", "fondue": "/ˈfɒnduː/", "zombie": "/ˈzɒmbɪ/", "locket": "/ˈlɒkɪt/", "ottoman": "/ˈɒtəmən/",
    "tiramisu": "/ˌtɪrəmɪˈsuː/", "cockatoo": "/ˌkɒkəˈtuː/", "manatee": "/ˌmænəˈtiː/", "mozzarella": "/ˌmɒtsəˈrelə/",
    "feta": "/ˈfetə/", "orangutan": "/ɔːˈræŋətæn/", "rapids": "/ˈræpɪdz/", "kumquat": "/ˈkʌmkwɒt/", "mason": "/ˈmeɪsn/",
    "trucker": "/ˈtrʌkə/",
    "cilantro": "/sɪˈlæntrəʊ/", "coffeehouse": "/ˈkɒfihaʊs/", "curbside": "/ˈkɜːbsaɪd/", "footwear": "/ˈfʊtweə/",
    "candlelight": "/ˈkændlaɪt/", "corduroy": "/ˈkɔːdərɔɪ/", "foil": "/fɔɪl/", "dumpster": "/ˈdʌmpstə/",
    "graffiti": "/ɡrəˈfiːtɪ/", "khakis": "/ˈkɑːkɪz/", "intercom": "/ˈɪntəkɒm/", "kiosk": "/ˈkiːɒsk/",
    "puree": "/ˈpjʊəreɪ/", "sketchbook": "/ˈsketʃbʊk/", "stairwell": "/ˈsteəwel/", "planetarium": "/ˌplænɪˈteərɪəm/",
    "sandbar": "/ˈsændbɑː/", "rhododendron": "/ˌrəʊdəˈdendrən/", "refill": "/ˈriːfɪl/",
    "glovebox": "/ˈɡlʌvbɒks/", "seatbelt": "/ˈsiːtbelt/", "steering wheel": "/ˈstɪərɪŋ wiːl/", "fuel gauge": "/ˈfjuːəl ɡeɪdʒ/",
    "handbrake": "/ˈhændbreɪk/", "hazard lights": "/ˈhæzəd laɪts/", "rear-view mirror": "/ˌrɪə vjuː ˈmɪrə/",
    "wing mirror": "/ˌwɪŋ ˈmɪrə/", "cup holder": "/ˈkʌp həʊldə/", "sun visor": "/ˈsʌn vaɪzə/", "airbag": "/ˈeəbæɡ/",
    "sunroof": "/ˈsʌnruːf/", "roof rack": "/ˈruːf ræk/", "number plate": "/ˈnʌmbə pleɪt/", "hatchback": "/ˈhætʃbæk/",
    "bull bar": "/ˈbʊl bɑː/", "jumper leads": "/ˈdʒʌmpə liːdz/", "car jack": "/ˈkɑː dʒæk/", "spare tyre": "/ˌspeə ˈtaɪə/",
    "flat tyre": "/ˌflæt ˈtaɪə/", "tow bar": "/ˈtəʊ bɑː/", "SUV": "/ˌes juː ˈviː/", "tow truck": "/ˈtəʊ trʌk/", "car wash": "/ˈkɑː wɒʃ/",
    "petrol station": "/ˈpetrəl steɪʃn/", "jerry can": "/ˈdʒeri kæn/", "carport": "/ˈkɑːpɔːt/",
    "parking meter": "/ˈpɑːkɪŋ miːtə/", "speed camera": "/ˈspiːd kæmərə/", "speed bump": "/ˈspiːd bʌmp/",
    "traffic lights": "/ˈtræfɪk laɪts/", "traffic jam": "/ˈtræfɪk dʒæm/", "stop sign": "/ˈstɒp saɪn/",
    "give way sign": "/ˌɡɪv ˈweɪ saɪn/", "zebra crossing": "/ˌzebrə ˈkrɒsɪŋ/", "roadworks": "/ˈrəʊdwɜːks/",
    "L plates": "/ˈel pleɪts/", "dashcam": "/ˈdæʃkæm/", "car seat": "/ˈkɑː siːt/", "drive-through": "/ˈdraɪv θruː/",
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
