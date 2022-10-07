import sys
from pathlib import Path

from neo4j import GraphDatabase


class WriteTaxonomy:
    """Write the taxonomy of the neo4j database into a file"""

    def __init__(self, uri="bolt://localhost:7687"):
        self.driver = GraphDatabase.driver(uri)
        # Doesn't create error even if there is no active database
        self.session = self.driver.session()

    def normalized_filename(self, filename):
        """add the .txt extension if it is missing in the filename"""
        return filename + (".txt" if (len(filename) < 4 or filename[-4:] != ".txt") else "")

    def create_multi_label(self, filename, branch_name):
        """Create a combined label with taxonomy name and branch name"""
        filename_without_extension = Path(filename).stem
        return ("t_" + filename_without_extension) + ":" + ("b_" + branch_name)

    def get_all_nodes(self, multi_label):
        """query the database and yield each node with its parents,
        this function use the relationships between nodes"""
        query = f"""
            MATCH path = ShortestPath(
                (h:{multi_label}:TEXT)-[:is_before*]->(f:{multi_label}:TEXT)
            )
            WHERE h.id="__header__" AND f.id="__footer__"
            UNWIND nodes(path) AS n
            RETURN n , [(n)-[:is_child_of]->(m) | m ]
        """
        results = self.session.run(query)
        for result in results:
            node, parents = result.values()
            yield node, parents

    def list_tags_lc(self, node):
        """return an ordered list of the language codes (lc) used in a node"""
        lc_list = []
        if "stopwords" in node["id"]:
            # stopwords node only have a tags_lc property
            key = "tags_"
            # number of dashes to split on to get language code
            dash_before_lc = 1
        else:
            key = "tags_ids_"
            dash_before_lc = 2

        for property in node:
            if property.startswith(key):
                lc_list.append(property.split("_", dash_before_lc)[dash_before_lc])
        lc_list.sort()
        return lc_list

    def get_tags_line(self, node, lc):
        """return a string that should look like the original line"""
        line = (", ").join(node["tags_" + lc])
        return lc + ":" + line

    def list_property_and_lc(self, node):
        """return a ordered list of properties with their language code (lc)"""
        # there is no rule for the order of properties
        # properties will be arranged in alphabetical order
        return [property[5:] for property in node if property.startswith("prop_")]

    def get_property_line(self, node, property):
        """return a string that should look like the original property line"""
        property_name, lc = property.rsplit("_", 1)
        property_value = node["prop_" + property]
        line = property_name + ":" + lc + ":" + property_value
        return line

    def get_parents_lines(self, parents):
        for parent in parents:
            parent = dict(parent)
            lc = parent["main_language"]
            parent_id = parent["tags_" + lc][0]
            yield "<" + lc + ":" + parent_id

    def iter_lines(self, multi_label):
        previous_block_id = ""
        for node, parents in self.get_all_nodes(multi_label):
            node = dict(node)
            has_content = node["id"] not in ["__header__", "__footer__"]
            # eventually add a blank line but in specific case
            following_synonyms = node["id"].startswith("synonyms") and previous_block_id.startswith(
                "synonyms"
            )
            following_stopwords = node["id"].startswith(
                "stopwords"
            ) and previous_block_id.startswith("stopwords")
            add_blank = has_content and not (following_synonyms or following_stopwords)
            if add_blank:
                yield ""
            # comments
            if node["preceding_lines"]:
                yield from node["preceding_lines"]
            if has_content:
                tags_lc = self.list_tags_lc(node)
                if node["id"].startswith("stopwords"):
                    yield "stopwords:" + self.get_tags_line(node, tags_lc[0])
                elif node["id"].startswith("synonyms"):
                    yield "synonyms:" + self.get_tags_line(node, tags_lc[0])
                else:
                    # synonyms line
                    yield from self.get_parents_lines(parents)
                    # main language synonyms first
                    main_language = node.pop("main_language")
                    tags_lc.remove(main_language)
                    yield self.get_tags_line(node, main_language)
                    # more synonyms after
                    for lc in tags_lc:
                        yield self.get_tags_line(node, lc)
                    # properties
                    properties_list = self.list_property_and_lc(node)
                    for property in properties_list:
                        yield self.get_property_line(node, property)
            previous_block_id = node["id"]

    def rewrite_file(self, filename, lines):
        """Write a .txt file with the given name"""
        filename = self.normalized_filename(filename)
        with open(filename, "w", encoding="utf8") as file:
            for line in lines:
                file.write(line + "\n")

    def __call__(self, filename, branch_name):
        filename = self.normalized_filename(filename)
        branch_name = self.normalizing(branch_name, char="_")
        multi_label = self.create_multi_label(filename, branch_name)
        lines = self.iter_lines(multi_label)
        self.rewrite_file(filename, lines)


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "test"
    branch_name = sys.argv[2] if len(sys.argv) > 1 else "branch"
    write = WriteTaxonomy()
    write(filename, branch_name)
