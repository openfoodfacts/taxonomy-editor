# Taxonomy parser

References: https://wiki.openfoodfacts.org/Global_taxonomies#format

This specification takes the imagine that we have a graph tool.
It can be in memory graph like networkx or custom dictionary structure.
Or a database, be it a real graph database like Arango db, or another database (eg. PostgresSQL) used with graph queries.

You must be able to query the database on it's relations, but also on nodes properties in an efficient way.

# Definitions

## Lines and blocks

1. a language code is a two character code. We write `LC` to signify a language code in this document.
1. every line has on of the following form:
   - *blank line*: it only contains space characters or no character at all
   - *comment line*: first character is a `#`
   - *parent line*: fist character is `<`
   - *entry line*: it begins with `LC:`
   - *stopwords line*: it begins with `stopwords:LC:`
   - *global synonyms line*: it begins with `synonyms:LC`
   - *property line*: it begins with a property_name
     (we will use `PN` to mean any property name)
     followed by a language code: `PN:LC:`

     Note that *comment lines* are not *blank lines*.
1. *meaningful lines* are : all lines type,
   but *blank line* and *comment line*
1. Each blank line begins a new block, but
    1. each *stopwords line* or *global synonyms line*
       should be considered a separated block,
       (with preceding comment lines)
    1. the first lines, up to the first *meaningful line*
       (but preceding comment lines) is the *header*
    1. other blocks must contains at least one *entry line*.
       We call them *entry blocks*
1. entry lines are composed of the `LC:` header,
   then a list of *tags* separated by a comma `,`.
   Comma without at least one space around are not separators.
1. each *tag* as a *normalized version* referred to as *tagid*
1. each *entry line* as a first tag which is referred to as *line tag*,
   and as *line tagid* for it's *normalized version*.
   *line tagid* is considered the identifier for this *entry line*,
   and must be unique.
1. the first *entry line* of each *entry block*
   is referred to as *canonical tag* (resp. *canonical tagid*)
   for this block.
   This is considered the identifier for this block, and must be unique.
1. the text in the *parent line* is composed of `LC:` followed by text.
   This text is referred to as the *parent tag*

## Sanitizing a line

Each line we read in the file must be sanitized.

This is the following process:

1. remove any space characters at end of line
   ```python
   line = line.rstrip()
   ```
1. replace `’` (typographique quote) to simple quote `'`
   ```python
   line = line.replace("’", "'")
   ```
1. replace commas that have no space around by a lower comma character
   and do the same for escaped comma (preceded by a `\`)
   (to distinguish them from commas acting as tags separators)
   ```python
   line = re.sub(r"(\d),(\d)", r"\1‚\2", line)
   line = re.sub(r"\\,", "\\‚", line)
   ```
1. removes parenthesis for roman numerals
   ```python
   line = re.sub(r"\(([ivx]+)\)", r"\1", line, flags=re.I)
   ```

## Normalized version of a string (of a tag)

The *normalized version* of a string is the operation
we will apply that to tag to obtain the tagid.

It depends on the language.

Obtain NFC form of the string. In python:
```python
string = unicodedata.normalize("NFC", my_input)
```

Then look at `string_normalization_for_lang` in `Config_off.pm` [^string_config]
to know if following operations applies, based on language code:
* lowercase
* removing accents

If lowercase applies and string is not a UUID, that is it does not match regexp `r"^[a-z\-]+\.[a-zA-Z0-9-_]{8}[a-zA-Z0-9-_]+$"`,
then lowercase it. And also transform "." to "-".

Replace every special character (ascii 0 to 27) and zero width space with "-":
```python
string = re.sub(r"[\u0000-\u0027\u200b]", "-", string)
```

Replace html escaped chars by "-":
```python
string = re.sub(r"&\w+;", "-", string)
```

Replace some weirds chars by "-" [^strech_weird_chars]:
```
string = re.sub(r"[\s!"#\$%&'()*+,\/:;<=>?@\[\\\]^_`{\|}~¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿×ˆ˜–—‘’‚“”„†‡•…‰‹›€™\t]", "-", string)
```

If removing accents applies, use `unidecode.unidecode` to remove them.

Finally, replace consecutive "-" by only one minus, and strip "-":
```python
string = re.sub(r"-+", "-", string)
string = string.strip("-")
```

[^string_config]: of course you would have copied it to a local config file, or a dict in your code.

[^strech_weird_chars]: (stretch goal: use [unicode category](https://www.compart.com/en/unicode/category) (through unicodedata module) to remove all unwanted category)

# Processing

## Harvest data

1. store the header in a node with id `__header__`
2. store each block of *stopwords line* in a node with id `stopwords:IDX` where `IDX` is the number of preceding *stopwords lines* in the file, and store inside:
   * every tag and tagid with language code included
3. store each block of *global synonyms line* in a node with id `synonyms:IDX` where `IDX` is the number of preceding *global synonyms lines* in the file, , and store inside:
   * every tag and tagid with language code included
2. For each entry block, create a node with id `LC:canonical_tagid`
   store inside:
   * every *property value* (a simple json)
   * every *parent tag* with their *tagid*, language code included (this is temporary)
   * every *tags*, with their *tagid*, language code included

For every node, also store:
* a specific `block_index` property which stores the number of blocks before this one in the file
* a specific `block_subindex` property which is always 0
  (such that if we want to insert a new block beneath this block,
  later on,
  we could insert it with same block_index but block_subindex of 1)
* preceding *comments lines* in a `preceeding_lines` property

## Create extended synonyms

TODO - This is a stretch goal for now

# Resolve parents

For every node in the graph, and for every parent tag entry it has,
create a link "is child of" with the node that has this tagid, (language code included).
This should correspond to a simple request in the database, which should be fast enough if data structure helps and correct indexes are set.

# Add additional properties

TODO - This is a stretch goal for now