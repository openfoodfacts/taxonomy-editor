from neo4j import GraphDatabase


class WriteFile:
    def __init__(self, uri="bolt://localhost:7687"):
        self.driver = GraphDatabase.driver(uri)
        self.session = (
            self.driver.session()
        )  # Doesn't create error even if there is no active database

    def normalized_filename(self, filename):
        """add the .txt extension if it is missing in the filename"""
        return filename + (
            ".txt" if (len(filename) < 4 or filename[-4:] != ".txt") else ""
        )

    def get_all_nodes(self):
        """query the database and yield each node with its parents,
        this function use the relationships between nodes"""
        query = """
            MATCH path = ShortestPath( (h:TEXT{id:"__header__"})-[:is_before*]->(f:TEXT{id:"__footer__"}) )
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
            part = 1
        else:
            key = "tags_ids_"
            part = 2

        for property in node:
            if property.startswith(key):
                lc_list.append(property.split("_", part)[part])
        lc_list.sort()
        return lc_list

    def write_tags_line(self, node, lc):
        """return a string that should look like the original line"""
        line = (", ").join(node["tags_" + lc])
        line = lc + ":" + line + "\n"
        return line

    def write_comment_lines(self, comments):
        """return a string that should look like the original comment lines"""
        lines = ("\n").join(comments)
        lines += "\n"
        return lines

    def list_property_and_lc(self, node):
        """return a ordered list of properties with their language code (lc)"""
        prop_list = []
        for property in node:
            if property.startswith("prop_"):
                prop_list.append(property[5:])

        # there is no rule for the order of properties
        # properties will be arranged in alphabetical order
        prop_list.sort()
        return prop_list

    def write_property(self, node, property):
        """return a string that should look like the original property line"""
        property_name, lc = property.rsplit("_", 1)
        property_value = node["prop_" + property]
        line = property_name + ":" + lc + ":" + property_value + "\n"
        return line

    def rewrite_file(self, filename):
        """Write a .txt file with the given name"""
        filename = self.normalized_filename(filename)
        nodes = self.get_all_nodes()
        previous_block = ""
        with open(filename, "w", encoding="utf8") as file:
            for node, parents in nodes:
                node = dict(node)
                txt = ""
                if node["preceding_lines"]:
                    txt += self.write_comment_lines(node.pop("preceding_lines"))
                if node["id"] not in ["__header__", "__footer__"]:
                    tags_lc = self.list_tags_lc(node)
                    if "stopwords" in node["id"]:
                        if not "stopwords" in previous_block:
                            txt = "\n" + txt
                        txt += "stopwords:" + self.write_tags_line(node, tags_lc[0])
                    elif "synonyms" in node["id"]:
                        if not "synonyms" in previous_block:
                            txt = "\n" + txt
                        txt += "synonyms:" + self.write_tags_line(node, tags_lc[0])
                    else:
                        if parents:
                            for parent in parents:
                                parent = dict(parent)
                                lc = parent["main_language"]
                                parent_id = parent["tags_" + lc][0]
                                txt += "<" + lc + ":" + parent_id + "\n"
                        txt = "\n" + txt
                        main_language = node.pop("main_language")
                        tags_lc.remove(main_language)
                        txt += self.write_tags_line(node, main_language)
                        for lc in tags_lc:
                            txt += self.write_tags_line(node, lc)
                        properties_list = self.list_property_and_lc(node)
                        for property in properties_list:
                            txt += self.write_property(node, property)
                previous_block = node["id"]
                file.write(txt)

    def __call__(self, filename):
        self.rewrite_file(filename)


if __name__ == "__main__":
    write = WriteFile()
    write("test")
