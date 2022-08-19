import logging
import re
import unicodedata

import unidecode
from neo4j import GraphDatabase

from .exception import DuplicateIDError


def ellipsis(text, max=20):
    """Cut a text adding eventual ellipsis if we do not display it fully"""
    return text[:max] + ("..." if len(text) > max else "")


class Parser:
    """Parse a taxonomy file and build a neo4j graph"""

    def __init__(self, uri="bolt://localhost:7687"):
        self.driver = GraphDatabase.driver(uri)
        self.session = (
            self.driver.session()
        )  # Doesn't create error even if there is no active database

    def create_headernode(self, header):
        """create the node for the header"""
        query = """
                CREATE (n:TEXT {id: '__header__' })
                SET n.preceding_lines= $header
                SET n.src_position= 1
            """
        self.session.run(query, header=header)

    def create_node(self, data):
        """run the query to create the node with data dictionary"""
        position_query = """
            SET n.is_before = $is_before
            SET n.preceding_lines= $preceding_lines
            SET n.src_position= $src_position
        """
        entry_query = ""
        if data["id"] == "__footer__":
            id_query = " CREATE (n:TEXT {id: $id }) \n "
        elif data["id"].startswith("synonyms"):
            id_query = " CREATE (n:SYNONYMS {id: $id }) \n "
        elif data["id"].startswith("stopwords"):
            id_query = " CREATE (n:STOPWORDS {id: $id }) \n "
        else:
            id_query = " CREATE (n:ENTRY {id: $id , main_language : $main_language}) \n "
            if data["parent_tag"]:
                entry_query += " SET n.parents = $parent_tag \n"
            for key in data:
                if key.startswith("prop_"):
                    entry_query += " SET n." + key + " = $" + key + "\n"

        for key in data:
            if key.startswith("tags_"):
                entry_query += " SET n." + key + " = $" + key + "\n"

        query = id_query + entry_query + position_query
        self.session.run(
            query,
            data,
            is_before=self.is_before,
        )

    def normalized_filename(self, filename):
        """add the .txt extension if it is missing in the filename"""
        return filename + (".txt" if (len(filename) < 4 or filename[-4:] != ".txt") else "")

    def file_iter(self, filename, start=0):
        """generator to get the file line by line"""
        with open(filename, "r", encoding="utf8") as file:
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
        yield line_number, ""  # to end the last entry if not ended

    def normalizing(self, line, lang="default"):
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
            r"[\s!\"#\$%&'()*+,\/:;<=>?@\[\\\]^_`{\|}~¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿×ˆ˜–—‘’‚“”„†‡•…‰‹›€™\t]",
            "-",
            line,
        )

        # removing excess "-"
        line = re.sub(r"-+", "-", line)
        line = line.strip("-")
        return line

    def remove_stopwords(self, lc, words):
        """to remove the stopwords that were read at the beginning of the file"""
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

    def add_line(self, line):
        """to get a normalized string but keeping the language code "lc:" , used for id and parent tag"""
        lc, line = line.split(":", 1)
        new_line = lc + ":"
        new_line += self.remove_stopwords(lc, self.normalizing(line, lc))
        return new_line

    def get_lc_value(self, line):
        """to get the language code "lc" and a list of normalized values"""
        lc, line = line.split(":", 1)
        new_line = []
        for word in line.split(","):
            new_line.append(self.remove_stopwords(lc, self.normalizing(word, lc)))
        return lc, new_line

    def new_node_data(self):
        """To create an empty dictionary that will be used to create node"""
        data = {
            "id": "",
            "main_language": "",
            "preceding_lines": [],
            "parent_tag": [],
            "src_position": None,
        }
        return data

    def set_data_id(self, data, id, line_number):
        if not data["id"]:
            data["id"] = id
        else:
            raise DuplicateIDError(line_number)
        return data

    def header_harvest(self, filename):
        """to harvest the header (comment with #), it has its own function because some header has multiple blocks"""
        h = 0
        header = []
        for _, line in self.file_iter(filename):
            if not (line) or line[0] == "#":
                header.append(line)
            else:
                break
            h += 1

        # we don't want to eat the comments of the next block and it removes the last separating line
        for i in range(len(header)):
            if header.pop():
                h -= 1
            else:
                break

        return header, h

    def entry_end(self, line, data):
        """Return True if the block ended"""
        # stopwords and synonyms are one-liner, entries are separated by a blank line
        if line.startswith("stopwords") or line.startswith("synonyms") or not line:
            # can be the end of an block or just additional line separator,
            # file_iter() always end with ''
            if data["id"]:  # to be sure that it's an end
                return True
        return False

    def remove_separating_line(self, data):
        """
        To remove the one separating line that is always there,
        between synonyms part and stopwords part and before each entry
        """
        # first, check if there is at least one preceding line
        if data["preceding_lines"] and not data["preceding_lines"][0]:
            if data["id"].startswith("synonyms"):
                # it's a synonyms block,
                # if the previous block is a stopwords block,
                # there is at least one separating line
                if "stopwords" in self.is_before:
                    data["preceding_lines"].pop(0)

            elif data["id"].startswith("stopwords"):
                # it's a stopwords block,
                # if the previous block is a synonyms block,
                # there is at least one separating line
                if "synonyms" in self.is_before:
                    data["preceding_lines"].pop(0)

            else:
                # it's an entry block, there is always a separating line
                data["preceding_lines"].pop(0)
        return data

    def harvest(self, filename):
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

        # header
        header, next_line = self.header_harvest(filename)
        yield header
        self.is_before = "__header__"

        # the other entries
        data = self.new_node_data()
        for line_number, line in self.file_iter(filename, next_line):
            # yield data if block ended
            if self.entry_end(line, data):
                if data["id"] in saved_nodes:
                    msg = f"Entry with same id {data['id']} already created, "
                    msg += f"duplicate id in file at line {data['src_position']}. "
                    msg += f"Node creation cancelled"
                    logging.error(msg)
                else:
                    data = self.remove_separating_line(data)
                    yield data  # another function will use this dictionary to create a node
                    self.is_before = data["id"]
                    saved_nodes.append(data["id"])
                data = self.new_node_data()

            # harvest the line
            if not (line) or line[0] == "#":
                # comment or blank
                data["preceding_lines"].append(line)
            else:
                line = line.rstrip(",")
                if not data["src_position"]:
                    data["src_position"] = line_number + 1
                if line.startswith("stopwords"):
                    # general stopwords definition for a language
                    id = "stopwords:" + str(index_stopwords)
                    data = self.set_data_id(data, id, line_number)
                    index_stopwords += 1
                    try:
                        lc, value = self.get_lc_value(line[10:])
                    except ValueError:
                        logging.error(
                            "Missing language code at line %d ? '%s'",
                            line_number + 1,
                            ellipsis(line),
                        )
                    else:
                        data["tags_" + lc] = value
                        # add the list with its lc
                        self.stopwords[lc] = value
                elif line.startswith("synonyms"):
                    # general synonyms definition for a language
                    id = "synonyms:" + str(index_synonyms)
                    data = self.set_data_id(data, id, line_number)
                    index_synonyms += 1
                    line = line[9:]
                    tags = [words.strip() for words in line[3:].split(",")]
                    try:
                        lc, value = self.get_lc_value(line)
                    except ValueError:
                        logging.error(
                            "Missing language code at line %d ? '%s'",
                            line_number + 1,
                            ellipsis(line),
                        )
                    else:
                        data["tags_" + lc] = tags
                        data["tags_ids_" + lc] = value
                elif line[0] == "<":
                    # parent definition
                    data["parent_tag"].append(self.add_line(line[1:]))
                elif language_code_prefix.match(line):
                    # synonyms definition
                    if not data["id"]:
                        data["id"] = self.add_line(line.split(",", 1)[0])
                        # first 2-3 characters before ":" are the language code
                        data["main_language"] = data["id"].split(":", 1)[0]
                    # add tags and tagsid
                    lang, line = line.split(":", 1)
                    # to transform '-' from language code to '_'
                    lang = lang.strip().replace("-", "_")
                    tags_list = []
                    tagsids_list = []
                    for word in line.split(","):
                        tags_list.append(word.strip())
                        word_normalized = self.remove_stopwords(lang, self.normalizing(word, lang))
                        if word_normalized not in tagsids_list:
                            # in case 2 normalized synonyms are the same
                            tagsids_list.append(word_normalized)
                    data["tags_" + lang] = tags_list
                    data["tags_ids_" + lang] = tagsids_list
                else:
                    # property definition
                    property_name = None
                    try:
                        property_name, lc, property_value = line.split(":", 2)
                    except ValueError:
                        logging.error(
                            "Reading error at line %d, unexpected format: '%s'",
                            line_number + 1,
                            ellipsis(line),
                        )
                    else:
                        # in case there is space before or after the colons
                        property_name = property_name.strip()
                        lc = lc.strip().replace("-", "_")
                        if not (
                            correctly_written.match(property_name) and correctly_written.match(lc)
                        ):
                            logging.error(
                                "Reading error at line %d, unexpected format: '%s'",
                                line_number + 1,
                                ellipsis(line),
                            )
                    if property_name:
                        data["prop_" + property_name + "_" + lc] = property_value

        data["id"] = "__footer__"
        data["preceding_lines"].pop(0)
        data["src_position"] = line_number + 1 - len(data["preceding_lines"])
        yield data

    def create_nodes(self, filename):
        """Adding nodes to database"""
        logging.info("Creating nodes")
        filename = self.normalized_filename(filename)
        harvested_data = self.harvest(filename)
        self.create_headernode(next(harvested_data))
        for entry in harvested_data:
            self.create_node(entry)

    def create_previous_link(self):
        logging.info("Creating 'is_before' links")
        query = "MATCH(n) WHERE exists(n.is_before) return n.id,n.is_before"
        results = self.session.run(query)
        for result in results:
            id = result["n.id"]
            id_previous = result["n.is_before"]

            query = """
                MATCH(n) WHERE n.id = $id
                MATCH(p) WHERE p.id= $id_previous
                CREATE (p)-[r:is_before]->(n)
                RETURN r
            """
            results = self.session.run(query, id=id, id_previous=id_previous)
            relation = results.values()
            if len(relation) > 1:
                logging.error(
                    "2 or more 'is_before' links created for ids %s and %s, "
                    "one of the ids isn't unique",
                    id,
                    id_previous,
                )
            elif not relation[0]:
                logging.error(
                    "link not created between %s and %s",
                    id,
                    id_previous,
                )

    def parent_search(self):
        """Get the parent and the child to link"""
        query = "match(n) WHERE size(n.parents)>0 return n.id, n.parents"
        results = self.session.run(query)
        for result in results:
            id = result["n.id"]
            parent_list = result["n.parents"]
            for parent in parent_list:
                yield parent, id

    def create_child_link(self):
        """Create the relations between nodes"""
        logging.info("Creating 'is_child_of' links")
        for parent, child_id in self.parent_search():
            lc, parent_id = parent.split(":")
            query = """ MATCH(p) WHERE $parent_id IN p.tags_ids_""" + lc
            query += """
                MATCH(c) WHERE c.id= $child_id
                CREATE (c)-[r:is_child_of]->(p)
                RETURN r
            """
            result = self.session.run(query, parent_id=parent_id, child_id=child_id)
            if not result.value():
                logging.warning(f"parent not found for child {child_id} with parent {parent_id}")

    def delete_used_properties(self):
        query = "MATCH (n) SET n.is_before = null, n.parents = null"
        self.session.run(query)

    def __call__(self, filename):
        """process the file"""
        self.create_nodes(filename)
        self.create_child_link()
        self.create_previous_link()
        # self.delete_used_properties()


if __name__ == "__main__":
    import sys

    logging.basicConfig(filename="parser.log", encoding="utf-8", level=logging.INFO)
    filename = sys.argv[1] if len(sys.argv) > 1 else "test"
    parse = Parser()
    parse(filename)
