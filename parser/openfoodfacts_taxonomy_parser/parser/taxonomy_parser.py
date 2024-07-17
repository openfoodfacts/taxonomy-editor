import collections
import copy
import logging
import re
import sys
import timeit
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator, TypedDict

from ..utils import normalize_filename, normalize_text
from .exception import DuplicateIDError
from .logger import ParserConsoleLogger


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
    parent_tags: list[tuple[str, int]] = field(default_factory=list)
    src_position: int | None = None
    properties: dict[str, str] = field(default_factory=dict)
    tags: dict[str, list[str]] = field(default_factory=dict)
    comments: dict[str, list[str]] = field(default_factory=dict)
    # comments_stack is a list of tuples (line_number, comment),
    # to keep track of comments just above the current line
    # during parsing of an entry, to be able to add them
    # to the right property or tag when possible
    comments_stack: list[tuple[int, str]] = field(default_factory=list)
    is_external: bool = False  # True if the node comes from another taxonomy
    original_taxonomy: str | None = None  # the name of the taxonomy the node comes from

    def to_dict(self):
        return {
            "id": self.id,
            "main_language": self.main_language,
            "preceding_lines": self.preceding_lines,
            "src_position": self.src_position,
            "is_external": self.is_external,
            "original_taxonomy": self.original_taxonomy,
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
    line_position: int


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
                # replace commas between digits and that have no space around by a lower comma character
                # and do the same for escaped comma (preceded by a \)
                # (to distinguish them from commas acting as tags separators)
                line = re.sub(r"(\d),(\d)", r"\1‚\2", line)
                line = re.sub(r"\\,", "\\‚", line)
                # removes parenthesis for roman numeral
                line = re.sub(r"\(([ivx]+)\)", r"\1", line, flags=re.I)
                yield line_number, line
                line_count += 1
            yield line_count, ""  # to end the last entry if not ended

    def _normalize_entry_id(self, raw_id: str) -> str:
        """
        Get a normalized string but keeping the language code "lc:",
        used for id and parent tag
        """
        lc, main_tag = raw_id.split(":", 1)
        normalized_main_tag = normalize_text(main_tag, lc, stopwords=self.stopwords)
        normalized_id = f"{lc}:{normalized_main_tag}"
        return normalized_id

    def undo_normalize_text(self, text: str) -> str:
        """Undo some normalizations made in `_file_iter`"""
        # restore commas from lower comma characters
        text = re.sub(r"(\d)‚(\d)", r"\1,\2", text)
        text = re.sub(r"\\‚", "\\,", text)
        return text

    def _get_lc_value(self, line: str) -> tuple[str, list[str]]:
        """Get the language code "lc" and a list of normalized values"""
        lc, line = line.split(":", 1)
        new_line: list[str] = []
        for word in line.split(","):
            new_line.append(normalize_text(word, lc, stopwords=self.stopwords))
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

    _language_code_prefix = re.compile(
        r"[a-zA-Z][a-zA-Z][a-zA-Z]?([-_][a-zA-Z][a-zA-Z][a-zA-Z]?)?:"
    )

    def is_entry_synonyms_line(self, line):
        matching_prefix = self._language_code_prefix.match(line)
        if matching_prefix:
            # verify it's not a property, that is a name followed by a colon and a language
            return not (
                self._language_code_prefix.match(line[matching_prefix.end():])
            )
        return False

    def _harvest_entries(self, filename: str, entries_start_line: int) -> Iterator[NodeData]:
        """Transform data from file to dictionary"""
        saved_nodes = []
        index_stopwords = 0
        index_synonyms = 0
        
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
                data = self._remove_separating_line(data)
                if data.get_node_type() == NodeType.ENTRY:
                    data = self._get_node_data_with_parent_and_end_comments(data)
                if data.id in saved_nodes:
                    # this duplicate node will be merged with the first one
                    data.is_before = None
                    msg = (
                        f"WARNING: Entry with same id {data.id} already exists, "
                        f"duplicate id in file at line {data.src_position}. "
                        "The two nodes will be merged, keeping the last "
                        "values in case of conflicts."
                    )
                    self.parser_logger.error(msg)
                else:
                    saved_nodes.append(data.id)
                    is_before = data.id
                yield data  # another function will use this dictionary to create a node
                data = NodeData(is_before=is_before)

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
                    tags = [self.undo_normalize_text(words.strip()) for words in line[3:].split(",")]
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
                    tags = [self.undo_normalize_text(words.strip()) for words in line[3:].split(",")]
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
                    data.parent_tags.append((self._normalize_entry_id(line[1:]), line_number + 1))
                elif self.is_entry_synonyms_line(line):
                    # synonyms definition
                    if not data.id:
                        data.id = self._normalize_entry_id(line.split(",", 1)[0])
                        # first 2-3 characters before ":" are the language code
                        data.main_language = data.id.split(":", 1)[0]
                    # add tags and tagsid
                    lang, line = line.split(":", 1)
                    # to transform '-' from language code to '_'
                    lang = lang.strip().replace("-", "_")
                    tags_list = []
                    tagsids_list = []
                    for word in line.split(","):
                        tags_list.append(self.undo_normalize_text(word.strip()))
                        word_normalized = normalize_text(word, lang, stopwords=self.stopwords)
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
                            data.properties[prop_key] = self.undo_normalize_text(property_value)
                            data = self._get_node_data_with_comments_above_key(
                                data, line_number, prop_key
                            )

        data.id = "__footer__"
        data.preceding_lines.pop(0)
        data.src_position = line_number + 1 - len(data.preceding_lines)
        yield data

    def _normalise_and_validate_child_links(
        self, entry_nodes: list[NodeData], unnormalised_child_links: list[ChildLink]
    ) -> tuple[list[ChildLink], list[ChildLink]]:
        # we need to group them by language code of the parent id
        lc_child_links_map = collections.defaultdict(list)
        for child_link in unnormalised_child_links:
            lc, _ = child_link["parent_id"].split(":")
            lc_child_links_map[lc].append(child_link)

        # we need to check if the parent id exists in the tags_ids_lc
        missing_child_links = []
        normalised_child_links = []
        for lc, lc_child_links in lc_child_links_map.items():
            # we collect all the tags_ids in a certain language
            tags_ids = {}
            for node in entry_nodes:
                node_tags_ids = {tag_id: node.id for tag_id in node.tags.get(f"tags_ids_{lc}", [])}
                tags_ids.update(node_tags_ids)

            # we check if the parent_id exists in the tags_ids
            for child_link in lc_child_links:
                _, parent_id = child_link["parent_id"].split(":")
                if parent_id not in tags_ids:
                    missing_child_links.append(child_link)
                else:
                    child_link["parent_id"] = tags_ids[parent_id]  # normalise the parent_id
                    normalised_child_links.append(child_link)

        return normalised_child_links, missing_child_links

    def _get_valid_child_links(
        self, entry_nodes: list[NodeData], raw_child_links: list[ChildLink]
    ) -> list[ChildLink]:
        """Get only the valid child links, i.e. the child links whose the parent_id exists"""
        node_ids = set([node.id for node in entry_nodes])

        # Links in which the parent_id exists are valid and do not need to be normalized
        valid_child_links = [
            child_link.copy()
            for child_link in raw_child_links
            if child_link["parent_id"] in node_ids
        ]

        # Unnormalised links are links in which a synonym was used to designate the parent
        child_links_to_normalise = [
            child_link.copy()
            for child_link in raw_child_links
            if child_link["parent_id"] not in node_ids
        ]

        # Normalise and validate the unnormalised links
        normalised_child_links, missing_child_links = self._normalise_and_validate_child_links(
            entry_nodes, child_links_to_normalise
        )

        valid_child_links.extend(normalised_child_links)

        for child_link in missing_child_links:
            lc, parent_id = child_link["parent_id"].split(":")
            self.parser_logger.error(
                f"Missing child link at line {child_link['line_position']}: "
                f"parent_id {parent_id} not found in tags_ids_{lc}"
            )

        return valid_child_links

    def _remove_duplicate_child_links(self, child_links: list[ChildLink]) -> list[ChildLink]:
        """Remove duplicate child links (i.e child links with the same parent_id and id)"""
        unique_child_links = []
        children_to_parents = collections.defaultdict(set)
        for child_link in child_links:
            parent_id, child_id = child_link["parent_id"], child_link["id"]
            if parent_id not in children_to_parents[child_id]:
                children_to_parents[child_id].add(parent_id)
                unique_child_links.append(child_link)
        return unique_child_links

    def _merge_duplicate_entry_nodes(self, entry_nodes: list[NodeData]) -> list[NodeData]:
        """Merge entry nodes with the same id:
        - merge their tags (union)
        - merge their properties (union, and in case of conflict, keep the last value)"""
        unique_entry_nodes = []
        ids_to_nodes = dict()
        for node in entry_nodes:
            if node.id in ids_to_nodes:
                first_node = ids_to_nodes[node.id]
                if first_node.is_external:
                    # we don't want to merge a node with an external node;
                    # the external node gets a new id with its original taxonomy name
                    # and the new one becomes the new "first node"
                    first_node.id += f"@{first_node.original_taxonomy}"
                    unique_entry_nodes.append(node)
                    ids_to_nodes[node.id] = node
                    continue
                for key, value in node.tags.items():
                    if not key.startswith("tags_ids_"):
                        # union of the tags
                        first_node.tags[key] = list(
                            # we use a dict to remove duplicates
                            # while keeping the order of the tags
                            dict.fromkeys(first_node.tags.get(key, []) + value)
                        )
                        # we have to re-normalize the tags_ids and can't just do a union,
                        # because two tags can have the same normalized value
                        language_code = key.split("_")[1]
                        first_node.tags[f"tags_ids_{language_code}"] = [
                            normalize_text(tag, language_code, stopwords=self.stopwords)
                            for tag in first_node.tags[key]
                        ]
                for key, value in node.properties.items():
                    # overwrite the value if the property already exists in the first node
                    first_node.properties[key] = value
                for key, value in node.comments.items():
                    # union of the comments
                    first_node.comments[key] = list(
                        # we use a dict to remove duplicates
                        # while keeping the order of the tags
                        dict.fromkeys(first_node.comments.get(key, []) + value)
                    )
                # union of the preceding_lines comments
                first_node.preceding_lines.extend(node.preceding_lines)
            else:
                unique_entry_nodes.append(node)
                ids_to_nodes[node.id] = node
        return unique_entry_nodes

    def _create_taxonomy(
        self, filename: str, external_filenames: list[str] | None = None
    ) -> Taxonomy:
        """Create the taxonomy from the file"""
        # parse external taxonomies if any, and add their entry nodes to the main taxonomy
        external_entry_nodes = []
        for external_filename in external_filenames or []:
            external_taxonomy_parser = TaxonomyParser()
            external_taxonomy = external_taxonomy_parser.parse_file(
                external_filename, None, self.parser_logger
            )
            external_entry_nodes.extend(external_taxonomy.entry_nodes)
        for node in external_entry_nodes:
            node.is_external = True

        self.parser_logger.info(f"Parsing {filename}")
        harvested_header_data, entries_start_line = self._header_harvest(filename)
        entry_nodes: list[NodeData] = []
        entry_nodes.extend(external_entry_nodes)
        other_nodes = [
            NodeData(id="__header__", preceding_lines=harvested_header_data, src_position=1)
        ]
        previous_links: list[PreviousLink] = []
        raw_child_links: list[ChildLink] = []
        harvested_data = self._harvest_entries(filename, entries_start_line)
        for entry in harvested_data:
            if entry.get_node_type() == NodeType.ENTRY:
                entry.original_taxonomy = filename.split("/")[-1]
                entry_nodes.append(entry)
            else:
                other_nodes.append(entry)
            if entry.is_before:
                previous_links.append(PreviousLink(before_id=entry.is_before, id=entry.id))
            if entry.parent_tags:
                for position, (parent, line_position) in enumerate(entry.parent_tags):
                    raw_child_links.append(
                        ChildLink(
                            parent_id=parent,
                            id=entry.id,
                            position=position,
                            line_position=line_position,
                        )
                    )
        valid_child_links = self._get_valid_child_links(entry_nodes, raw_child_links)
        child_links = self._remove_duplicate_child_links(valid_child_links)
        entry_nodes = self._merge_duplicate_entry_nodes(entry_nodes)
        return Taxonomy(
            entry_nodes=entry_nodes,
            other_nodes=other_nodes,
            previous_links=previous_links,
            child_links=child_links,
        )

    def parse_file(
        self,
        filename: str,
        external_filenames: list[str] | None = None,
        logger: ParserConsoleLogger | None = None,
    ) -> Taxonomy:
        if logger:
            self.parser_logger = logger
        """Process the file into a Taxonomy object"""
        start_time = timeit.default_timer()
        filename = normalize_filename(filename)
        taxonomy = self._create_taxonomy(filename, external_filenames)
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
