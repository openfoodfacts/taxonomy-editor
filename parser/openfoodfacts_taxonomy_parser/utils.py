import re
import unicodedata

import unidecode


def normalize_text(
    line: str,
    lang: str = "default",
    char: str = "-",
    stopwords: dict[str, list[str]] | None = None,
) -> str:
    """Normalize a string depending on the language code"""
    if stopwords is None:
        stopwords = {}

    # replace ’ (typographique quote) to simple quote '
    line = line.replace("’", "'")
    # removes parenthesis for roman numeral
    line = re.sub(r"\(([ivx]+)\)", r"\1", line, flags=re.I)

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

    # Remove stopwords
    if lang in stopwords:
        stopwords = stopwords[lang]
        line_surrounded_by_char = char + line + char
        for stopword in stopwords:
            line_surrounded_by_char = line_surrounded_by_char.replace(char + stopword + char, char)
        line = line_surrounded_by_char[1:-1]

    return line


def normalize_filename(filename: str) -> str:
    """add the .txt extension if it is missing in the filename"""
    return filename + (".txt" if (len(filename) < 4 or filename[-4:] != ".txt") else "")


def get_project_name(taxonomy_name: str, branch_name: str) -> str:
    """Create a project name for given branch and taxonomy"""
    return "p_" + taxonomy_name + "_" + branch_name


def src_lines(src_lines_str: list[str]):
    for line in src_lines_str:
        start, end = line.split(",")
        yield int(start), int(end)
