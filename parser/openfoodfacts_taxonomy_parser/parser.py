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
        tags_prefixed_lc = ["n.tags_" + lc for lc in language_codes]
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

    def check(self, limit_big_parent=50, threshold_language=3):
        # check taxonomy
        self.check_roots()
        self.check_big_parents(limit_big_parent)

        # check entries
        self.check_shortest_and_longest_path()
        self.check_number_of_descendants()
        self.check_parents_prop()
        self.check_children()

        # check language
        self.check_language(threshold_language)
        self.check_synonyms()

    def check_roots(self):
        """Add the number and the list of root nodes in a 'taxonomy' node"""
        query = 'MERGE (n:CHECK{id:"taxonomy"}) '
        self.session.run(query)
        query = """ 
            MATCH(n:ENTRY) 
            WHERE not (n)-[:is_child_of]->() 
            WITH count(n) AS number, collect(n.id) as list 
            MATCH(p:CHECK{id:"taxonomy"}) 
            SET p.root_number = number 
            SET p.root_list = list 
        """
        self.session.run(query)

    def check_big_parents(self, limit=50):
        """Add the list of the 'limit' (default 50) nodes with the most children"""
        query = 'MERGE (n:CHECK{id:"taxonomy"}) '
        self.session.run(query)
        query = """
            MATCH ()-[r:is_child_of]->(n) 
            WITH n, count(r) AS number 
            ORDER BY number DESC 
            LIMIT $limit
            WITH [n.id,toString(number)] AS parent 
            UNWIND parent AS parents
            WITH collect(parents) AS result
            MATCH(p:CHECK{id:"taxonomy"}) 
            SET p.big_parents = result
        """
        self.session.run(query, limit=limit)

    def check_shortest_and_longest_path(self):
        """Add to entry node, if it has parent,
        its shortest path and longest path to a root"""
        query = """
        MATCH path = (n:ENTRY)-[:is_child_of*]->(root:ENTRY)
        WHERE not (root)-[:is_child_of]->(:ENTRY)
        WITH path,length(path) as len, n
        ORDER BY len
        WITH collect(path) as p, n
        WITH nodes(p[0]) AS short, size(nodes(p[0])) AS shortlen,
            nodes(p[-1]) AS long, size(nodes(p[-1])) AS longlen, n
        SET n.stat_shortest_path = [x in short | x.id]
        SET n.stat_shortest_path_length = shortlen
        SET n.stat_longest_path = [x in long | x.id]
        SET n.stat_longest_path_length = longlen
        """
        self.session.run(query)

    def check_number_of_descendants(self):
        """Add the number of descendants to all nodes with children"""
        query = """
            MATCH (c)-[:is_child_of*]->(n:ENTRY)
            WITH n,count(DISTINCT c) AS number
            SET n.stat_number_of_descendants = number
        """
        self.session.run(query)

    def dictionary_to_list(self, dictionary):
        """Convert a dictionary of lists to a list where each key is followed by its value"""
        list_dictionary = []
        for key in dictionary:
            if not dictionary[key]:
                continue
            list_dictionary.append(key)
            list_dictionary.extend(dictionary[key])
        return list_dictionary

    def add_parent_prop_query(self, child, prop_parent, prop_redefined):
        """query the database to add parent related properties"""
        query = """
            MATCH (c)
            WHERE c.id = $child_id
            SET c.stat_parents_prop = $parent_prop
            SET c.stat_parents_redefined_prop = $redefined_prop
        """
        data = {"child_id": child["id"]}
        data["parent_prop"] = self.dictionary_to_list(prop_parent)
        data["redefined_prop"] = self.dictionary_to_list(prop_redefined)
        self.session.run(query, data)

    def check_parents_prop(self):
        """Add 'properties from parents' property and 'redefined properties' property,
        adds [] if there is none
        """
        query = """
            MATCH (c:ENTRY)-[:is_child_of]->(p:ENTRY) 
            RETURN  c,collect(p)
        """
        results = self.session.run(query)
        for result in results:
            child, parents = result.values()
            prop_parents = {}
            prop_redefined = {}
            for parent in parents:
                id = parent["id"]
                prop_parents[id] = []
                prop_redefined[id] = []
                for property in parent:
                    if property.startswith("prop_"):
                        if property in child:
                            prop_redefined[id].append(property)
                        else:
                            prop_parents[id].append(property)
            self.add_parent_prop_query(child, prop_parents, prop_redefined)

    def add_child_stat_query(self, parent, prop_redefined, number, missing_lc):
        """query the database to add child related properties"""
        query = """
            MATCH (p)
            WHERE p.id = $parent_id
            SET p.stat_children_redefined_prop = $redefined_prop
            SET p.stat_children_using_synonyms = $number
            SET p.stat_missing_translation = $missing_lc
        """
        data = {"parent_id": parent["id"]}
        data["redefined_prop"] = self.dictionary_to_list(prop_redefined)
        data["number"] = number
        data["missing_lc"] = self.dictionary_to_list(missing_lc)
        self.session.run(query, data)

    def list_tags_lc(self, node):
        """return a list of language codes (lc) used in the node tags"""
        lc_list = []
        for property in node:
            if property.startswith("tags_ids_"):
                lc_list.append(property.split("_", 2)[2])
        return lc_list

    def check_children(self):
        """Adds 'stat_children_redefined_prop', a list of children and their redefined properties
        Adds 'stat_children_using_synonyms', the number of children not using the parent id
        Adds 'stat_missing_translation', a list of languages used by children but not the entry
        """
        query = """
            MATCH (c:ENTRY)-[:is_child_of]->(p:ENTRY) 
            RETURN  collect(c),p
        """
        results = self.session.run(query)
        for result in results:
            children, parent = result.values()
            using_synonyms = 0
            prop_redefined = {}
            parent_lc = self.list_tags_lc(parent)
            missing_lc = {}
            for child in children:
                if parent["id"] not in child["parents"]:
                    using_synonyms += 1
                id = child["id"]
                prop_redefined[id] = []
                for property in child:
                    if property.startswith("prop_"):
                        if property in parent:
                            prop_redefined[id].append(property)
                    elif property.startswith("tags_ids_"):
                        child_lc = property.split("_", 2)[2]
                        if child_lc not in parent_lc:
                            if child_lc not in missing_lc:
                                missing_lc[child_lc] = [child["id"]]
                            else:
                                missing_lc[child_lc].append(child["id"])
            self.add_child_stat_query(
                parent, prop_redefined, using_synonyms, missing_lc
            )

    def check_language(self, threshold=3):
        """Add nodes with the percentage of translation in each language
        and a list a tags used in multiple entries"""
        query = "MATCH (n:ENTRY) RETURN n"
        results = self.session.run(query)

        # dictionary that will contain all the tags for each language
        all_tags = {}
        # dictionary that will contain repeated tags for each language
        reused_tags = {}
        # dictionary used to track the number of translated nodes for each language
        language = {}
        # total number of nodes
        number_of_nodes = 0
        # number of nodes with at least 3 translations
        nodes_with_3translations = 0
        # list of nodes (their id) with less than 3 translations
        nodes_missing_translation = []

        # Counting
        for result in results:
            number_of_nodes += 1
            node = result.value()
            number_of_translation = 0
            for property in node:
                if property.startswith("tags_ids_"):
                    lc = property.split("_", 2)[2]

                    # check if a tag is already used in another entry
                    all_tags.setdefault(lc, [])
                    tags = node[property]
                    for tag in tags:
                        if tag in all_tags[lc]:
                            reused_tags.setdefault(lc, [])
                            if tag not in reused_tags[lc]:
                                reused_tags[lc].append(tag)
                    all_tags[lc].extend(tags)

                    # count number of translation
                    number_of_translation += 1
                    language.setdefault(lc, 0)
                    language[lc] += 1

            if number_of_translation < threshold:
                nodes_missing_translation.append(node["id"])
            else:
                nodes_with_3translations += 1

        percentage_translated = nodes_with_3translations / number_of_nodes * 100
        language = {k: v / number_of_nodes * 100 for k, v in language.items()}

        # Adding the result in the database
        # First the main language node with general information
        query = """
            CREATE (main:CHECK {id : '__language__'})
            SET main.nodes_missing_translation = $list
            SET main.percentage_with_3_translations_or_more = $percentage
        """
        self.session.run(
            query, list=nodes_missing_translation, percentage=percentage_translated
        )

        # Then all the sub-nodes for every language with their percentage and repeated tags
        tags_list = None  # create variable
        for lc in language:
            query = f"CREATE (n:CHECK{{id:'{lc}',percentage: ${lc} }}) \n"
            if lc in reused_tags:
                query += "SET n.multiple_use = $tags_list "
                tags_list = reused_tags[lc]
            self.session.run(query, language, tags_list=tags_list)
        query = """
            MATCH(main:CHECK {id : '__language__'})
            MATCH(n:CHECK) WHERE not n=main
            CREATE (n)-[:from]->(main)
        """
        self.session.run(query)

    def tags_use_synonyms(self, tags, synonyms):
        """check if a list of tags contains one or more synonyms and count them"""
        synonyms_use_count = [0 for i in range(len(synonyms))]
        for tag in tags:
            for i, group in enumerate(synonyms):
                for synonym in group:
                    if synonym in tag:
                        synonyms_use_count[i] += 1
        return synonyms_use_count

    def check_synonyms(self):
        """Check the usage of each synonyms defined in the synonyms nodes"""
        # get the synonyms from the database
        query = "MATCH (n:SYNONYMS) return n"
        results = self.session.run(query)
        # dictionary that will contain the synonyms for each language
        synonyms = {}
        # associate dictionary to count usage of each synonyms
        # register the total number of use and the number of entries that use them
        counter_synonyms_use = {}
        for result in results:
            node = result.value()
            for property in node:
                if property.startswith("tags_ids_"):
                    lc = property.split("_", 2)[2]
                    synonyms.setdefault(lc, [])
                    counter_synonyms_use.setdefault(lc, [])
                    synonyms[lc].append(node[property])
                    counter_synonyms_use[lc].append([0, 0])

        # check if synonyms are used and count
        query = "MATCH (n:ENTRY) return n"
        results = self.session.run(query)
        for result in results:
            node = result.value()
            for property in node:
                if property.startswith("tags_ids_"):
                    lc = property.split("_", 2)[2]
                    if lc in synonyms:
                        tags = node[property]
                        add = self.tags_use_synonyms(tags, synonyms[lc])
                        for i in range(len(counter_synonyms_use[lc])):
                            if add[i]:
                                counter_synonyms_use[lc][i][0] += add[i]
                                counter_synonyms_use[lc][i][1] += 1

        # add the data on synonyms usage to their respective node
        for lc in synonyms:
            for i, synonym in enumerate(synonyms[lc]):
                query = f""" MATCH(n:SYNONYMS) 
                    WHERE n.tags_ids_{lc} = $synonym
                    SET n.used_total = $total
                    SET n.used_in_different_entries = $entries
                """
                data = {"synonym": synonym}
                data["total"] = counter_synonyms_use[lc][i][0]
                data["entries"] = counter_synonyms_use[lc][i][1]
                self.session.run(query, data)


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
