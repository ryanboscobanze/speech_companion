# text_utils.py
import re
import requests
import logging
from wordfreq import word_frequency

def is_potentially_difficult(word):
    if not word.isalpha():
        return False
    return word_frequency(word.lower(), "en") < 5e-6

def get_definition(word):
    try:
        response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data[0]["meanings"][0]["definitions"][0]["definition"]
        else:
            logging.warning(f"⚠️ No definition found for: {word} (status: {response.status_code})")
    except Exception as e:
        logging.exception(f"❌ Error fetching definition for: {word}")
    return None

def extract_named_entities(doc):
    return ", ".join(ent.text for ent in doc.ents)

def extract_clean_concepts(doc):
    ent_texts = set(ent.text.lower() for ent in doc.ents)
    concepts = set()
    for chunk in doc.noun_chunks:
        clean = chunk.text.lower().strip()
        clean = re.sub(r"[^\w\s]", "", clean)
        if clean in ent_texts:
            continue
        if chunk.root.pos_ not in ("PRON", "DET") and not chunk.root.is_stop:
            if len(clean) > 2 and not clean.startswith("the "):
                concepts.add(chunk.root.lemma_.lower())
    for token in doc:
        if token.pos_ in ("NOUN", "PROPN", "ADJ") and not token.is_stop and token.is_alpha:
            lemma = token.lemma_.lower()
            if lemma not in ent_texts and len(lemma) > 2:
                concepts.add(lemma)
    return ", ".join(sorted(concepts))

def extract_difficult_definitions(txt):
    words = re.findall(r"\b\w+\b", txt)
    found_defs = []
    try:
        for word in set(words):
            if is_potentially_difficult(word):
                definition = get_definition(word)
                if definition:
                    found_defs.append(f"{word}: {definition}")
        return "\n\n".join(found_defs) if found_defs else "—"
    except Exception as e:
        logging.exception(f"❌ Failed to extract difficult word definitions for: {txt}")
        return "❌ Error extracting definitions"

def detect_ambiguity(utterance: str) -> bool:
    utterance = utterance.lower().strip()
    if len(utterance.split()) < 4:
        return False
    ambiguity_signals = [
        r"\bi (don’t|can't|cannot)?\s?(remember|get|know|recall)\b.*\b(name|term|word|thing|what)\b",
        r"\bwhat('?s| is) it called\b",
        r"\bnot sure\b",
        r"\bi'm drawing a blank\b",
        r"\bthe word for it\b",
        r"\btip of (my|the) tongue\b",
        r"\bit'?s (kind of|something|sort of) like\b",
        r"\bthe thing that\b",
        r"\bsimilar to\b",
    ]
    return any(re.search(pat, utterance) for pat in ambiguity_signals)

def detect_hesitation(utterance: str) -> bool:
    utterance = utterance.lower()
    hesitation_signals = [
        r"\buh+\b", r"\bum+\b", r"\ber+\b",
        r"\blike\b", r"\byou know\b", r"\bwell,\b",
        r"\bkind of\b", r"\bso like\b", r"\.\.\."
    ]
    hits = sum(bool(re.search(pattern, utterance)) for pattern in hesitation_signals)
    return hits >= 2
