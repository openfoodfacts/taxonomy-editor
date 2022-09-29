import re
import unicodedata
import unidecode

def normalizing(line, lang="default"):
    """normalize a string depending of the language code lang"""
    line = unicodedata.normalize("NFC", line)

    # removing accent
    if lang in ["fr", "ca", "es", "it", "nl", "pt", "sk", "en"]:
        line = re.sub(r"[¢£¤¥§©ª®°²³µ¶¹º¼½¾×‰€™]", "-", line)
        line = unidecode.unidecode(line)

    # lower case except if language in list
    if lang not in []:
        line = line.lower()

    # changing unwanted character to "-"
    line = re.sub(r"[\u0000-\u0027\u200b]", "-", line)
    line = re.sub(r"&\w+;", "-", line)
    line = re.sub(
        r"[\s!\"#\$%&'()*+,\/:;<=>?@\[\\\]^_`{\|}~¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿×ˆ˜–—‘’‚“”„†‡•…‰‹›€™\t]",  # noqa: E501
        "-",
        line,
    )

    # removing excess "-"
    line = re.sub(r"-+", "-", line)
    line = line.strip("-")
    return line
