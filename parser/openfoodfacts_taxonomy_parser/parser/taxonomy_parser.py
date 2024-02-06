import copy
import logging
import re
import sys
import timeit
from enum import Enum
from dataclasses import dataclass, field
from typing import Iterator, TypedDict

from .logger import ParserConsoleLogger
from .exception import DuplicateIDError
from ..utils import normalize_filename, normalize_text


class NodeType(str, Enum):
    TEXT = "TEXT"
    SYNONYMS = "SYNONYMS"
    STOPWORDS = "STOPWORDS"
    ENTRY = "ENTRY"


@dataclass(slots=True)
class NodeData:
    id: str = ""
    is_before: str | None = None
    main_language: str | None = None
    preceding_lines: list[str] = field(default_factory=list)
    parent_tags: list[str] = field(default_factory=list)
    src_position: int | None = None
    properties: dict[str, str] = field(default_factory=dict)
    tags: dict[str, list[str]] = field(default_factory=dict)
    comments: dict[str, list[str]] = field(default_factory=dict)
    # comments_stack is a list of tuples (line_number, comment),
    # to keep track of comments just above the current line
    # during parsing of an entry, to be able to add them
    # to the right property or tag when possible
    comments_stack: list[(int, str)] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id,
            "main_language": self.main_language,
            "preceding_lines": self.preceding_lines,
            "src_position": self.src_position,
            **self.properties,
            **self.tags,
            **self.comments,
        }

    def get_node_type(self):
        if self.id in ["__header__", "__footer__"]:
            return NodeType.TEXT
        elif self.id.startswith("synonyms"):
            return NodeType.SYNONYMS
        elif self.id.startswith("stopwords"):
            return NodeType.STOPWORDS
        else:
            return NodeType.ENTRY


class PreviousLink(TypedDict):
    before_id: str
    id: str


class ChildLink(TypedDict):
    parent_id: str
    id: str
    position: int


@dataclass(slots=True)
class Taxonomy:
    entry_nodes: list[NodeData]
    other_nodes: list[NodeData]
    previous_links: list[PreviousLink]
    child_links: list[ChildLink]


class TaxonomyParser:
    """Parse a taxonomy file"""

    def __init__(self):
        self.parser_logger = ParserConsoleLogger()

    def _file_iter(self, filename: str, start: int = 0) -> Iterator[tuple[int, str]]:
        """Generator to get the file line by line"""
        with open(filename, "r", encoding="utf8") as file:
            line_count = 0
            for line_number, line in enumerate(file):
                if line_number < start:
                    continue
                # sanitizing
                # remove any space characters at end of line
                line = line.rstrip()
                # replace ’ (typographique quote) to simple quote '
                line = line.replace("’", "'")
                # replace commas that have no space around by a lower comma character
                # and do the same for escaped comma (preceded by a \)
                # (to distinguish them from commas acting as tags separators)
                line = re.sub(r"(\d),(\d)", r"\1‚\2", line)
                line = re.sub(r"\\,", "\\‚", line)
                # removes parenthesis for roman numeral
                line = re.sub(r"\(([ivx]+)\)", r"\1", line, flags=re.I)
                yield line_number, line
                line_count += 1
            yield line_count, ""  # to end the last entry if not ended

    def _remove_stopwords(self, lc: str, words: str) -> str:
        """Remove the stopwords that were read at the beginning of the file"""
        # First check if this language has stopwords
        if lc in self.stopwords:
            words_to_remove = self.stopwords[lc]
            new_words = []
            for word in words.split("-"):
                if word not in words_to_remove:
                    new_words.append(word)
            return ("-").join(new_words)
        else:
            return words

    def _add_line(self, line: str) -> str:
        """
        Get a normalized string but keeping the language code "lc:",
        used for id and parent tag
        """
        lc, line = line.split(":", 1)
        new_line = lc + ":"
        new_line += self._remove_stopwords(lc, normalize_text(line, lc))
        return new_line

    def _get_lc_value(self, line: str) -> tuple[str, list[str]]:
        """Get the language code "lc" and a list of normalized values"""
        lc, line = line.split(":", 1)
        new_line: list[str] = []
        for word in line.split(","):
            new_line.append(self._remove_stopwords(lc, normalize_text(word, lc)))
        return lc, new_line

    def _set_data_id(self, data: NodeData, id: str, line_number: int) -> NodeData:
        if not data.id:
            data.id = id
        else:
            raise DuplicateIDError(line_number)
        return data

    def _header_harvest(self, filename: str) -> tuple[list[str], int]:
        """
        Harvest the header (comment with #),
        it has its own function because some header has multiple blocks
        """
        h = 0
        header: list[str] = []
        for _, line in self._file_iter(filename):
            if not (line) or line[0] == "#":
                header.append(line)
            else:
                break
            h += 1

        # we don't want to eat the comments of the next block
        # and it removes the last separating line
        for i in range(len(header)):
            if header.pop():
                h -= 1
            else:
                break

        return header, h

    def _entry_end(self, line: str, data: NodeData) -> bool:
        """Return True if the block ended"""
        if data.id.startswith("stopwords") or data.id.startswith("synonyms"):
            # stopwords and synonyms are one-liners; if the id is set, it's the end
            return True
        if not line and data.id:
            # entries are separated by a blank line
            return True
        return False

    def _remove_separating_line(self, data: NodeData) -> NodeData:
        """
        To remove the one separating line that is always there,
        between synonyms part and stopwords part and before each entry
        """
        is_before = data.is_before
        # first, check if there is at least one preceding line
        if data.preceding_lines and not data.preceding_lines[0]:
            if data.id.startswith("synonyms"):
                # it's a synonyms block,
                # if the previous block is a stopwords block,
                # there is at least one separating line
                if is_before and "stopwords" in is_before:
                    data.preceding_lines.pop(0)

            elif data.id.startswith("stopwords"):
                # it's a stopwords block,
                # if the previous block is a synonyms block,
                # there is at least one separating line
                if is_before and "synonyms" in is_before:
                    data.preceding_lines.pop(0)

            else:
                # it's an entry block, there is always a separating line
                data.preceding_lines.pop(0)
        return data

    def _get_node_data_with_comments_above_key(
        self, data: NodeData, line_number: int, key: str
    ) -> NodeData:
        """Returns the updated node data with comments above the given
        key stored in the {key}_comments property."""
        new_data = copy.deepcopy(data)

        # Get comments just above the given line
        comments_above = []
        current_line = line_number - 1
        while new_data.comments_stack and new_data.comments_stack[-1][0] == current_line:
            comments_above.append(new_data.comments_stack.pop()[1])
            current_line -= 1
        if comments_above:
            new_data.comments[key + "_comments"] = comments_above[::-1]

        return new_data

    def _get_node_data_with_parent_and_end_comments(self, data: NodeData) -> NodeData:
        """Returns the updated node data with parent and end comments"""
        new_data = copy.deepcopy(data)

        # Get parent comments (part of an entry block and just above/between the parents lines)
        parent_comments = []
        while new_data.preceding_lines and new_data.preceding_lines[-1] != "":
            parent_comments.append(new_data.preceding_lines.pop())
        if parent_comments:
            new_data.comments["parent_comments"] = parent_comments[::-1]

        # Get end comments (part of an entry block after the last tag/prop
        # and before the separating blank line)
        end_comments = [comment[1] for comment in new_data.comments_stack]
        if end_comments:
            new_data.comments["end_comments"] = end_comments

        return new_data

    def _harvest_entries(self, filename: str, entries_start_line: int) -> Iterator[NodeData]:
        """Transform data from file to dictionary"""
        saved_nodes = []
        index_stopwords = 0
        index_synonyms = 0
        language_code_prefix = re.compile(
            r"[a-zA-Z][a-zA-Z][a-zA-Z]?([-_][a-zA-Z][a-zA-Z][a-zA-Z]?)?:"
        )
        # Check if it is correctly written
        correctly_written = re.compile(r"\w+\Z")
        # stopwords will contain a list of stopwords with their language code as key
        self.stopwords = {}
        # the other entries
        data = NodeData(is_before="__header__")
        line_number = (
            entries_start_line  # if the iterator is empty, line_number will not be unbound
        )
        for line_number, line in self._file_iter(filename, entries_start_line):
            # yield data if block ended
            if self._entry_end(line, data):
                if data.id in saved_nodes:
                    msg = (
                        f"Entry with same id {data.id} already created, "
                        f"duplicate id in file at line {data.src_position}. "
                        "Node creation cancelled."
                    )
                    self.parser_logger.error(msg)
                else:
                    data = self._remove_separating_line(data)
                    if data.get_node_type() == NodeType.ENTRY:
                        data = self._get_node_data_with_parent_and_end_comments(data)
                    yield data  # another function will use this dictionary to create a node
                    saved_nodes.append(data.id)
                data = NodeData(is_before=data.id)

            # harvest the line
            if not (line) or line[0] == "#":
                # comment or blank line
                if data.id:
                    # we are within the node definition
                    data.comments_stack.append((line_number, line))
                else:
                    # we are before the actual node
                    data.preceding_lines.append(line)
            else:
                line = line.rstrip(",")
                if not data.src_position:
                    data.src_position = line_number + 1
                if line.startswith("stopwords"):
                    # general stopwords definition for a language
                    id = "stopwords:" + str(index_stopwords)
                    data = self._set_data_id(data, id, line_number)
                    index_stopwords += 1
                    # remove "stopwords:" part
                    line = line[10:]
                    # compute raw values outside _get_lc_value as it normalizes them!
                    tags = [words.strip() for words in line[3:].split(",")]
                    try:
                        lc, value = self._get_lc_value(line)
                    except ValueError:
                        self.parser_logger.error(
                            f"Missing language code at line {line_number + 1} ? '{self.parser_logger.ellipsis(line)}'"
                        )
                    else:
                        data.tags["tags_" + lc] = tags
                        data.tags["tags_ids_" + lc] = value
                        # add the normalized list with its lc
                        self.stopwords[lc] = value
                elif line.startswith("synonyms"):
                    # general synonyms definition for a language
                    id = "synonyms:" + str(index_synonyms)
                    data = self._set_data_id(data, id, line_number)
                    index_synonyms += 1
                    # remove "synonyms:" part
                    line = line[9:]
                    # compute raw values outside _get_lc_value as it normalizes them!
                    tags = [words.strip() for words in line[3:].split(",")]
                    try:
                        lc, value = self._get_lc_value(line)
                    except ValueError:
                        self.parser_logger.error(
                            f"Missing language code at line {line_number + 1} ? '{self.parser_logger.ellipsis(line)}'"
                        )
                    else:
                        data.tags["tags_" + lc] = tags
                        data.tags["tags_ids_" + lc] = value
                elif line[0] == "<":
                    # parent definition
                    data.parent_tags.append(self._add_line(line[1:]))
                elif language_code_prefix.match(line):
                    # synonyms definition
                    if not data.id:
                        data.id = self._add_line(line.split(",", 1)[0])
                        # first 2-3 characters before ":" are the language code
                        data.main_language = data.id.split(":", 1)[0]
                    # add tags and tagsid
                    lang, line = line.split(":", 1)
                    # to transform '-' from language code to '_'
                    lang = lang.strip().replace("-", "_")
                    tags_list = []
                    tagsids_list = []
                    for word in line.split(","):
                        tags_list.append(word.strip())
                        word_normalized = self._remove_stopwords(lang, normalize_text(word, lang))
                        if word_normalized not in tagsids_list:
                            # in case 2 normalized synonyms are the same
                            tagsids_list.append(word_normalized)
                    data.tags["tags_" + lang] = tags_list
                    data.tags["tags_ids_" + lang] = tagsids_list
                    data = self._get_node_data_with_comments_above_key(
                        data, line_number, "tags_" + lang
                    )
                else:
                    # property definition
                    property_name = None
                    try:
                        property_name, lc, property_value = line.split(":", 2)
                    except ValueError:
                        self.parser_logger.error(
                            f"Reading error at line {line_number + 1}, unexpected format: '{self.parser_logger.ellipsis(line)}'"
                        )
                    else:
                        # in case there is space before or after the colons
                        property_name = property_name.strip()
                        lc = lc.strip().replace("-", "_")
                        if not (
                            correctly_written.match(property_name) and correctly_written.match(lc)
                        ):
                            self.parser_logger.error(
                                f"Reading error at line {line_number + 1}, unexpected format: '{self.parser_logger.ellipsis(line)}'"
                            )
                        if property_name:
                            prop_key = "prop_" + property_name + "_" + lc
                            data.properties[prop_key] = property_value
                            data = self._get_node_data_with_comments_above_key(
                                data, line_number, prop_key
                            )

        data.id = "__footer__"
        data.preceding_lines.pop(0)
        data.src_position = line_number + 1 - len(data.preceding_lines)
        yield data

    def _create_taxonomy(self, filename: str) -> Taxonomy:
        """Create the taxonomy from the file"""
        self.parser_logger.info(f"Parsing {filename}")
        harvested_header_data, entries_start_line = self._header_harvest(filename)
        entry_nodes: list[NodeData] = []
        other_nodes = [
            NodeData(id="__header__", preceding_lines=harvested_header_data, src_position=1)
        ]
        previous_links: list[PreviousLink] = []
        child_links: list[ChildLink] = []
        harvested_data = self._harvest_entries(filename, entries_start_line)
        for entry in harvested_data:
            if entry.get_node_type() == NodeType.ENTRY:
                entry_nodes.append(entry)
            else:
                other_nodes.append(entry)
            if entry.is_before:
                previous_links.append(PreviousLink(before_id=entry.is_before, id=entry.id))
            if entry.parent_tags:
                for position, parent in enumerate(entry.parent_tags):
                    child_links.append(ChildLink(parent_id=parent, id=entry.id, position=position))
        return Taxonomy(
            entry_nodes=entry_nodes,
            other_nodes=other_nodes,
            previous_links=previous_links,
            child_links=child_links,
        )

    def parse_file(self, filename: str, logger: ParserConsoleLogger | None = None) -> Taxonomy:
        if logger:
            self.parser_logger = logger
        """Process the file into a Taxonomy object"""
        start_time = timeit.default_timer()
        filename = normalize_filename(filename)
        taxonomy = self._create_taxonomy(filename)
        self.parser_logger.info(f"Parsing done in {timeit.default_timer() - start_time} seconds.")
        self.parser_logger.info(
            f"Found {len(taxonomy.entry_nodes) + len(taxonomy.other_nodes)} nodes"
        )
        self.parser_logger.info(f"Found {len(taxonomy.previous_links)} previous links")
        self.parser_logger.info(f"Found {len(taxonomy.child_links)} child links")

        return taxonomy


if __name__ == "__main__":
    # Setup logs
    logging.basicConfig(handlers=[logging.StreamHandler()], level=logging.INFO)
    filename = sys.argv[1] if len(sys.argv) > 1 else "test"

    # Pass session variable to parser object
    parse = TaxonomyParser()
    parse.parse_file(filename)
