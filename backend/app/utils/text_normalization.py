import re
import unicodedata


def normalize_text(text: str) -> str:
    """Cleans a raw bank label so it can be reliably compared.

    Strips accents, uppercases, drops stray symbols, collapses whitespace.
    Bank statement labels are messy by nature (mixed case, accents, extra
    spaces) — normalizing first means every matcher downstream compares
    like-for-like instead of re-implementing this cleanup itself.
    """
    if not isinstance(text, str):
        return ""

    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    text = text.upper()
    text = re.sub(r"[^A-Z0-9\s\.\'\&\-\/\*\#]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
