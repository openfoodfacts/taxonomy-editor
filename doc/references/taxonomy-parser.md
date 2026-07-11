# Taxonomy parser

References: https://wiki.openfoodfacts.org/Global_taxonomies#format

This specification assumes that we have a graph tool.
It can be in memory graph like networkx or custom dictionary structure.
Or a database, be it a real graph database like Arango db, or another database (eg. PostgresSQL) used with graph queries.

You must be able to query the database on it's relations, but also on nodes properties in an efficient way.

# Definitions

## Lines and blocks

1. a language code is a two character code. We write `LC` to signify a language code in this document.
1. every line has one of the following forms:

   - _blank line_: it only contains space characters or no character at all
   - _comment line_: first character is a `#`
   - _parent line_: fist character is `<`
   - _entry line_: it begins with `LC:`
   - _stopwords line_: it begins with `stopwords:LC:`
   - _global synonyms line_: it begins with `synonyms:LC`
   - _property line_: it begins with a property_name
     (we will use `PN` to mean any property name)
     followed by a language code: `PN:LC:`

     Note that _comment lines_ are not _blank lines_.

1. _meaningful lines_ are : all lines type,
   but _blank line_ and _comment line_
1. Each blank line begins a new block, but
   1. each _stopwords line_ or _global synonyms line_
      should be considered a separated block,
      (with preceding comment lines)
   1. the first lines, up to the first _meaningful line_
      (but preceding comment lines) is the _header_
   1. the last lines, after the last _meaningful line_ in the file
      is the _footer_
   1. other blocks must contains at least one _entry line_.
      We call them _entry blocks_
1. entry lines are composed of the `LC:` header,
   then a list of _tags_ separated by a comma `,`.
   Comma without at least one space around are not separators.
1. each _tag_ has a _normalized version_ which is referred to as _tagid_
1. each _entry line_ has a first tag which is referred to as _line tag_,
   and as _line tagid_ for it's _normalized version_.
   _line tagid_ is considered the identifier for this _entry line_,
   and must be unique.
1. the first _entry line_ of each _entry block_
   is referred to as _canonical tag_ (resp. _canonical tagid_)
   for this block.
   This is considered the identifier for this block, and must be unique.
1. the text in the _parent line_ is composed of `LC:` followed by text.
   This text is referred to as the _parent tag_

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

The _normalized version_ of a string is the operation
we will apply that to tag to obtain the tagid.

It depends on the language.

Obtain NFC form of the string. In python:

```python
string = unicodedata.normalize("NFC", my_input)
```

Then look at `string_normalization_for_lang` in `Config_off.pm` [^string_config]
to know if following operations applies, based on language code:

- lowercase
- removing accents

If lowercase applies and string is not a UUID [^uuid], that is it does not match regexp `r"^[a-z\-]+\.[a-zA-Z0-9-_]{8}[a-zA-Z0-9-_]+$"`,
then lowercase it. And also transform "." to "-".

Replace every special character (ascii 0 to 27) and zero width space with "-":

```python
string = re.sub(r"[\u0000-\u0027\u200b]", "-", string)
```

Replace html escaped chars by "-":

```python
string = re.sub(r"&\w+;", "-", string)
```

Replace some strange characters with "-" [^stretch_weird_chars]:

```
string = re.sub(r"[\s!"#\$%&'()*+,\/:;<=>?@\[\\\]^_`{\|}~¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿×ˆ˜–—‘’‚“”„†‡•…‰‹›€™\t]", "-", string)
```

If removing accents applies, use `unidecode.unidecode` to remove them.

Finally, replace consecutive "-" by only one minus, and strip "-":

```python
string = re.sub(r"-+", "-", string)
string = string.strip("-")
```

[^uuid]:
    an UUID stands for Universal Unique Identifier.
    **TODO** explain when we may encounter them in taxonomies.

[^string_config]:
    of course you would have copied it to a local config file, or a dict in your code.
    The current config can be seen in github [openfoodfacts/openfoodfacts-server main/lib/ProductOpener/Config_off.pm](https://github.com/openfoodfacts/openfoodfacts-server/blob/main/lib/ProductOpener/Config_off.pm).
    Looking at `%string_normalization_for_lang`.

[^stretch_weird_chars]: (stretch goal: use [unicode category](https://www.compart.com/en/unicode/category) (through unicodedata module) to remove all unwanted category)

# Processing

## Harvest data

1. store the header in a node with id `__header__` and label TEXT
1. store the footer in a node with id `__footer__` and label TEXT
1. store each block of _stopwords line_ in a node with id `stopwords:IDX`
   and label STOPWORDS,
   where `IDX` is the number of preceding _stopwords lines_ in the file
1. store each block of _global synonyms line_
   in a node with id `synonyms:IDX`
   and label SYNONYMS,
   where `IDX` is the number of preceding _global synonyms lines_
   in the file
1. For each entry block, create a node with id `LC:canonical_tagid`
   and label ENTRY
   store inside:
   - every _property value_ in an attribute named prop_PROP_NAME_LC
   - a _main_language_ property which contains the LC of the canonical_tagid (aka entry id)
   - temporarily store every _parent tag_ with their _tagid_,
     language code included (you can remove it after link creations)

For every node but header and footer, store:

- tags_LC stores a list of tag for language LC
- tags_ids_LC stores a list of tagids for language LC

Note that synonyms and stopwords only have one language, while entry block may have several.

For every node, also store:

- preceding _comments lines_ in a `preceding_lines` property
- the start of the entry block in a property `src_position`. First line is 1.
  Comments (aka `preceding_lines`) are not accounted as block start, but for footer and header.

We also add a `is_before` link between nodes, to keep order in which nodes were found in the file.

- `__header__` should only have one outgoing `is_before` relation
- `__footer__` should only have one incoming `is_before` relation
- every other node should have exactly one incoming and one outgoing `is_before` relation

## Create extended synonyms

TODO - This is a stretch goal for now

# Resolve parents

For every node in the graph, and for every parent tag entry it has,
create a link "is child of" with the node that has this tagid, (language code included).
This should correspond to a simple request in the database, which should be fast enough if data structure helps and correct indexes are set.

# Add additional properties

TODO - This is a stretch goal for now
