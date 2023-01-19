import logging
import os
import re
import sys

import iso639
from neo4j import GraphDatabase

from .exception import DuplicateIDError
from .normalizer import normalizing


def ellipsis(text, max=20):
    """Cut a text adding eventual ellipsis if we do not display it fully"""
    return text[:max] + ("..." if len(text) > max else "")


class ParserConsoleLogger:
    def __init__(self):
        self.parsing_warnings = []  # Stores all warning logs
        self.parsing_errors = []  # Stores all error logs

    def info(self, msg, *args, **kwargs):
        """Stores all parsing info logs"""
        logging.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Stores all parsing warning logs"""
        self.parsing_warnings.append(msg % args)
        logging.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Stores all parsing error logs"""
        self.parsing_errors.append(msg % args)
        logging.error(msg, *args, **kwargs)


class Parser:
    """Parse a taxonomy file and build a neo4j graph"""

    def __init__(self, session):
        self.session = session
        self.parser_logger = ParserConsoleLogger()

    def create_headernode(self, header, multi_label):
        """Create the node for the header"""
        query = f"""
                CREATE (n:{multi_label}:TEXT)
                SET n.id = '__header__'
                SET n.preceding_lines= $header
                SET n.src_position= 1
            """
        self.session.run(query, header=header)

    def create_node(self, data, multi_label):
        """Run the query to create the node with data dictionary"""
        position_query = """
            SET n.id = $id
            SET n.is_before = $is_before
            SET n.preceding_lines = $preceding_lines
            SET n.src_position = $src_position
        """
        entry_query = ""
        if data["id"] == "__footer__":
            id_query = f" CREATE (n:{multi_label}:TEXT) \n "
        elif data["id"].startswith("synonyms"):
            id_query = f" CREATE (n:{multi_label}:SYNONYMS) \n "
        elif data["id"].startswith("stopwords"):
            id_query = f" CREATE (n:{multi_label}:STOPWORDS) \n "
        else:
            id_query = f" CREATE (n:{multi_label}:ENTRY) \n "
            position_query += " SET n.main_language = $main_language "
            if data["parent_tag"]:
                entry_query += " SET n.parents = $parent_tag \n"
            for key in data:
                if key.startswith("prop_"):
                    entry_query += " SET n." + key + " = $" + key + "\n"

        for key in data:
            if key.startswith("tags_"):
                entry_query += " SET n." + key + " = $" + key + "\n"

        query = id_query + entry_query + position_query
        self.session.run(query, data)

    def normalized_filename(self, filename):
        """Add the .txt extension if it is missing in the filename"""
        return filename + (".txt" if (len(filename) < 4 or filename[-4:] != ".txt") else "")

    def get_project_name(self, taxonomy_name, branch_name):
        """Create a project name for given branch and taxonomy"""
        return "p_" + taxonomy_name + "_" + branch_name

    def create_multi_label(self, taxonomy_name, branch_name):
        """Create a combined label with taxonomy name and branch name"""
        project_name = self.get_project_name(taxonomy_name, branch_name)
        return project_name + ":" + ("t_" + taxonomy_name) + ":" + ("b_" + branch_name)

    def file_iter(self, filename, start=0):
        """Generator to get the file line by line"""
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

    def remove_stopwords(self, lc, words):
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

    def add_line(self, line):
        """
        Get a normalized string but keeping the language code "lc:",
        used for id and parent tag
        """
        lc, line = line.split(":", 1)
        new_line = lc + ":"
        new_line += self.remove_stopwords(lc, normalizing(line, lc))
        return new_line

    def get_lc_value(self, line):
        """Get the language code "lc" and a list of normalized values"""
        lc, line = line.split(":", 1)
        new_line = []
        for word in line.split(","):
            new_line.append(self.remove_stopwords(lc, normalizing(word, lc)))
        return lc, new_line

    def new_node_data(self, is_before):
        """To create an empty dictionary that will be used to create node"""
        data = {
            "id": "",
            "main_language": "",
            "preceding_lines": [],
            "parent_tag": [],
            "src_position": None,
            "is_before": is_before,
        }
        return data

    def set_data_id(self, data, id, line_number):
        if not data["id"]:
            data["id"] = id
        else:
            raise DuplicateIDError(line_number)
        return data

    def header_harvest(self, filename):
        """
        Harvest the header (comment with #),
        it has its own function because some header has multiple blocks
        """
        h = 0
        header = []
        for _, line in self.file_iter(filename):
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
        is_before = data["is_before"]
        # first, check if there is at least one preceding line
        if data["preceding_lines"] and not data["preceding_lines"][0]:
            if data["id"].startswith("synonyms"):
                # it's a synonyms block,
                # if the previous block is a stopwords block,
                # there is at least one separating line
                if "stopwords" in is_before:
                    data["preceding_lines"].pop(0)

            elif data["id"].startswith("stopwords"):
                # it's a stopwords block,
                # if the previous block is a synonyms block,
                # there is at least one separating line
                if "synonyms" in is_before:
                    data["preceding_lines"].pop(0)

            else:
                # it's an entry block, there is always a separating line
                data["preceding_lines"].pop(0)
        return data

    def harvest(self, filename):
        """Transform data from file to dictionary
        """
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

        # the other entries
        data = self.new_node_data(is_before="__header__")
        data["is_before"] = "__header__"
        for line_number, line in self.file_iter(filename, next_line):
            # yield data if block ended
            if self.entry_end(line, data):
                if data["id"] in saved_nodes:
                    msg = (
                        "Entry with same id %s already created, "
                         "duplicate id in file at line %s. "
                         "Node creation cancelled."
                    )
                    self.parser_logger.error(msg, data['id'], data['src_position'])
                else:
                    data = self.remove_separating_line(data)
                    yield data  # another function will use this dictionary to create a node
                    saved_nodes.append(data["id"])
                data = self.new_node_data(is_before=data["id"])

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
                        self.parser_logger.error(
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
                        self.parser_logger.error(
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
                        word_normalized = self.remove_stopwords(lang, normalizing(word, lang))
                        if word_normalized not in tagsids_list:
                            # in case 2 normalized synonyms are the same
                            tagsids_list.append(word_normalized)
                    data["tags_" + lang] = tags_list
                    data["tags_" + lang + "_str"] = " ".join(tags_list)
                    data["tags_ids_" + lang] = tagsids_list
                else:
                    # property definition
                    property_name = None
                    try:
                        property_name, lc, property_value = line.split(":", 2)
                    except ValueError:
                        self.parser_logger.error(
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
                            self.parser_logger.error(
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

    def create_nodes(self, filename, multi_label):
        """Adding nodes to database"""
        self.parser_logger.info("Creating nodes")
        harvested_data = self.harvest(filename)
        self.create_headernode(next(harvested_data), multi_label)
        for entry in harvested_data:
            self.create_node(entry, multi_label)

    def create_previous_link(self, multi_label):
        self.parser_logger.info("Creating 'is_before' links")
        query = f"MATCH(n:{multi_label}) WHERE n.is_before IS NOT NULL return n.id, n.is_before"
        results = self.session.run(query)
        for result in results:
            id = result["n.id"]
            id_previous = result["n.is_before"]

            query = f"""
                MATCH(n:{multi_label}) WHERE n.id = $id
                MATCH(p:{multi_label}) WHERE p.id= $id_previous
                CREATE (p)-[r:is_before]->(n)
                RETURN r
            """
            results = self.session.run(query, id=id, id_previous=id_previous)
            relation = results.values()
            if len(relation) > 1:
                self.parser_logger.error(
                    "2 or more 'is_before' links created for ids %s and %s, "
                    "one of the ids isn't unique",
                    id,
                    id_previous,
                )
            elif not relation[0]:
                self.parser_logger.error("link not created between %s and %s", id, id_previous)

    def parent_search(self, multi_label):
        """Get the parent and the child to link"""
        query = f"MATCH (n:{multi_label}:ENTRY) WHERE SIZE(n.parents)>0 RETURN n.id, n.parents"
        results = self.session.run(query)
        for result in results:
            id = result["n.id"]
            parent_list = result["n.parents"]
            for parent in parent_list:
                yield parent, id

    def create_child_link(self, multi_label):
        """Create the relations between nodes"""
        self.parser_logger.info("Creating 'is_child_of' links")
        for parent, child_id in self.parent_search(multi_label):
            lc, parent_id = parent.split(":")
            query = f""" MATCH (p:{multi_label}:ENTRY) WHERE $parent_id IN p.tags_ids_""" + lc
            query += f"""
                MATCH (c:{multi_label}) WHERE c.id= $child_id
                CREATE (c)-[r:is_child_of]->(p)
                RETURN r
            """
            result = self.session.run(query, parent_id=parent_id, child_id=child_id)
            if not result.value():
                self.parser_logger.warning(
                    f"parent not found for child {child_id} with parent {parent_id}"
                )

    def delete_used_properties(self):
        query = "MATCH (n) SET n.is_before = null, n.parents = null"
        self.session.run(query)

    def create_fulltext_index(self, taxonomy_name, branch_name):
        """Create indexes for search"""
        project_name = self.get_project_name(taxonomy_name, branch_name)
        query = [
            f"""CREATE FULLTEXT INDEX {project_name+'_SearchIds'} IF NOT EXISTS
            FOR (n:{project_name}) ON EACH [n.id]\n"""
        ]
        query.append("""OPTIONS {indexConfig: {`fulltext.analyzer`: 'keyword'}}""")
        self.session.run("".join(query))

        language_codes = [lang.alpha2 for lang in list(iso639.languages) if lang.alpha2 != ""]
        tags_prefixed_lc = ["n.tags_" + lc + "_str" for lc in language_codes]
        tags_prefixed_lc = ", ".join(tags_prefixed_lc)
        query = f"""CREATE FULLTEXT INDEX {project_name+'_SearchTags'} IF NOT EXISTS
            FOR (n:{project_name}) ON EACH [{tags_prefixed_lc}]"""
        self.session.run(query)

    def create_parsing_errors_node(self, taxonomy_name, branch_name):
        """Create node to list parsing errors"""
        multi_label = self.create_multi_label(taxonomy_name, branch_name)
        query = f"""
            CREATE (n:{multi_label}:ERRORS)
            SET n.id = $project_name
            SET n.branch_name = $branch_name
            SET n.taxonomy_name = $taxonomy_name
            SET n.created_at = datetime()
            SET n.warnings = $warnings_list
            SET n.errors = $errors_list
        """
        params = {
            "project_name": self.get_project_name(taxonomy_name, branch_name),
            "branch_name": branch_name,
            "taxonomy_name": taxonomy_name,
            "warnings_list": self.parser_logger.parsing_warnings,
            "errors_list": self.parser_logger.parsing_errors,
        }
        self.session.run(query, params)

    def __call__(self, filename, branch_name, taxonomy_name):
        """Process the file"""
        filename = self.normalized_filename(filename)
        branch_name = normalizing(branch_name, char="_")
        multi_label = self.create_multi_label(taxonomy_name, branch_name)
        self.create_nodes(filename, multi_label)
        self.create_child_link(multi_label)
        self.create_previous_link(multi_label)
        self.create_fulltext_index(taxonomy_name, branch_name)
        self.create_parsing_errors_node(taxonomy_name, branch_name)
        # self.delete_used_properties()


if __name__ == "__main__":
    # Setup logs
    logging.basicConfig(handlers=[logging.StreamHandler()], level=logging.INFO)
    filename = sys.argv[1] if len(sys.argv) > 1 else "test"
    branch_name = sys.argv[2] if len(sys.argv) > 1 else "branch"
    taxonomy_name = sys.argv[3] if len(sys.argv) > 1 else filename.rsplit(".", 1)[0]

    # Initialize neo4j
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    driver = GraphDatabase.driver(uri)
    session = driver.session()

    # Pass session variable to parser object
    parse = Parser(session)
    parse(filename, branch_name, taxonomy_name)
