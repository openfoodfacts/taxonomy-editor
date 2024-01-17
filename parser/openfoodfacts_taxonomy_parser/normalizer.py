"""
String normalizer
"""
import re
import unicodedata

import unidecode


def normalizing(line: str, lang="default", char="-"):
    """Normalize a string depending on the language code"""
    line = unicodedata.normalize("NFC", line)

    # Removing accent
    if lang in ["fr", "ca", "es", "it", "nl", "pt", "sk", "en"]:
        line = re.sub(r"[¢£¤¥§©ª®°²³µ¶¹º¼½¾×‰€™]", char, line)
        line = unidecode.unidecode(line)

    # Lower case except if language in list
    if lang not in []:
        line = line.lower()

    # Changing unwanted character to "-"
    line = re.sub(r"[\u0000-\u0027\u200b]", char, line)
    line = re.sub(r"&\w+;", char, line)
    line = re.sub(
        r"[\s!\"#\$%&'()*+,\/:;<=>?@\[\\\]^_`{\|}~¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿×ˆ˜–—‘’‚“”„†‡•…‰‹›€™\t]",  # noqa: E501
        char,
        line,
    )

    # Removing excess "-"
    line = re.sub(r"-+", char, line)
    line = line.strip(char)
    return line
