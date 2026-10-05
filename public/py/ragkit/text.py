"""Normalización y tokenización de texto en español e inglés."""

import re
import unicodedata

_STOPWORDS_ES_RAW = """
a al algo ante antes aqui como con cual cuando de del desde donde el ella ellas ellos en entre era
es esa ese eso esta estan este esto fue ha han hasta hay la las le les lo los mas me mi mis mucho
muy ni no nos nosotros o otro para pero poco por porque que quien se sea ser si sin sobre su sus
tambien te tengo tiene todo tu tus un una uno unos y ya yo
"""

_STOPWORDS_EN_RAW = """
a an and are as at be but by for from has have he her his i in is it its me my not of on or our
she so that the their them they this to us was we were what when where which who will with you your
"""


def strip_accents(text: str) -> str:
    """Quita los acentos pero conserva la ñ ("año" no se confunde con "ano")."""
    out = []
    for ch in unicodedata.normalize("NFD", text):
        if unicodedata.category(ch) == "Mn" and ch != "̃":
            continue
        out.append(ch)
    return unicodedata.normalize("NFC", "".join(out))


def normalize(text: str) -> str:
    """Minúsculas y sin acentos."""
    return strip_accents(text.lower())


STOPWORDS_ES = frozenset(normalize(_STOPWORDS_ES_RAW).split())
STOPWORDS_EN = frozenset(normalize(_STOPWORDS_EN_RAW).split())

_TOKEN_RE = re.compile(r"[a-zñ0-9]+")


def tokenize(text: str, language: str = "es", remove_stopwords: bool = True) -> list[str]:
    """Divide un texto en tokens de palabras normalizados.

    >>> tokenize("¿Cuánto tarda el reembolso de mi pedido?")
    ['cuanto', 'tarda', 'reembolso', 'pedido']
    """
    tokens = _TOKEN_RE.findall(normalize(text))
    if not remove_stopwords:
        return tokens
    stop = STOPWORDS_ES if language == "es" else STOPWORDS_EN
    return [t for t in tokens if t not in stop]
