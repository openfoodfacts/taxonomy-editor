from neo4j import GraphDatabase
import re, unicodedata, unidecode
from .exception import DuplicateIDError


class Parser:
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
            id_query = (
                " CREATE (n:ENTRY {id: $id , main_language : $main_language}) \n "
            )
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
        return filename + (
            ".txt" if (len(filename) < 4 or filename[-4:] != ".txt") else ""
        )

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
        index_stopwords = 0
        index_synonyms = 0
        language_code_prefix = re.compile("[a-zA-Z][a-zA-Z][a-zA-Z]?:")
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
                data = self.remove_separating_line(data)
                yield data  # another function will use this dictionary to create a node
                self.is_before = data["id"]
                data = self.new_node_data()

            # harvest the line
            if not (line) or line[0] == "#":
                data["preceding_lines"].append(line)
            else:
                if not data["src_position"]:
                    data["src_position"] = line_number + 1
                if line.startswith("stopwords"):
                    id = "stopwords:" + str(index_stopwords)
                    data = self.set_data_id(data, id, line_number)
                    index_stopwords += 1
                    lc, value = self.get_lc_value(line[10:])
                    data["tags_" + lc] = value
                    # add the list with its lc
                    self.stopwords[lc] = value
                elif line.startswith("synonyms"):
                    id = "synonyms:" + str(index_synonyms)
                    data = self.set_data_id(data, id, line_number)
                    index_synonyms += 1
                    line = line[9:]
                    tags = [words.strip() for words in line[3:].split(",")]
                    lc, value = self.get_lc_value(line)
                    data["tags_" + lc] = tags
                    data["tags_ids_" + lc] = value
                elif line[0] == "<":
                    data["parent_tag"].append(self.add_line(line[1:]))
                elif language_code_prefix.match(line):
                    if not data["id"]:
                        data["id"] = self.add_line(line.split(",", 1)[0])
                        # first 2-3 characters before ":" are the language code
                        data["main_language"] = data["id"].split(":", 1)[0]  
                    # add tags and tagsid
                    lang, line = line.split(":", 1)
                    tags_list = []
                    tagsids_list = []
                    for word in line.split(","):
                        tags_list.append(word.strip())
                        word_normalized = self.remove_stopwords(
                            lang, self.normalizing(word, lang)
                        )
                        tagsids_list.append(word_normalized)
                    data["tags_" + lang] = tags_list
                    data["tags_ids_" + lang] = tagsids_list
                else:
                    property_name, lc, property_value = line.split(":", 2)
                    data["prop_" + property_name + "_" + lc] = property_value
        data["id"] = "__footer__"
        data["preceding_lines"].pop(0)
        data["src_position"] = line_number + 1 - len(data["preceding_lines"])
        yield data

    def create_nodes(self, filename):
        """Adding nodes to database"""
        filename = self.normalized_filename(filename)
        harvested_data = self.harvest(filename)
        self.create_headernode(next(harvested_data))
        for entry in harvested_data:
            self.create_node(entry)

    def create_previous_link(self):
        query = "MATCH(n) WHERE exists(n.is_before) return n.id,n.is_before"
        results = self.session.run(query)
        for result in results:
            id = result["n.id"]
            id_previous = result["n.is_before"]

            query = """
                MATCH(n) WHERE n.id = $id
                MATCH(p) WHERE p.id= $id_previous
                CREATE (p)-[:is_before]->(n)
            """
            self.session.run(query, id=id, id_previous=id_previous)

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
        for parent, child_id in self.parent_search():
            lc, parent_id = parent.split(":")
            tags_ids = "tags_ids_" + lc
            query = """ MATCH(p) WHERE $parent_id IN p.tags_ids_""" + lc
            query += """
                MATCH(c) WHERE c.id= $child_id
                CREATE (c)-[:is_child_of]->(p)
            """
            self.session.run(
                query, parent_id=parent_id, tagsid=tags_ids, child_id=child_id
            )

    def delete_used_properties(self):
        query = "MATCH (n) SET n.is_before = null, n.parents = null"
        self.session.run(query)

    def __call__(self, filename):
        """process the file"""
        self.create_nodes(filename)
        self.create_child_link()
        self.create_previous_link()
        # self.delete_used_properties()

    def check(self):
        #check taxonomy
        self.check_roots()
        self.check_big_parents()

        #check entries
        self.check_shortest_and_longest_path()
        self.check_number_of_descendants()
        self.check_parents_prop()
        self.check_children()

        #check language
        self.check_language()
        self.check_synonyms()

    def check_roots(self):
        """Add the number and the list of root nodes in a 'taxonomy' node"""
        query = 'MERGE (n:CHECK{id:"taxonomy"}) '
        self.session.run(query)
        query = """ 
            MATCH(n:ENTRY) 
            WHERE not ()-[:is_child_of]->(n) 
            WITH count(n) AS number, collect(n.id) as list 
            MATCH(p:CHECK{id:"taxonomy"}) 
            SET p.root_number = number 
            SET p.root_list = list 
        """
        self.session.run(query)
    
    def check_big_parents(self,limit=50):
        """Add the list of the 'limit' (default 50) nodes with the most children"""
        query = 'MERGE (n:CHECK{id:"taxonomy"}) '
        self.session.run(query)
        query = """
            MATCH ()-[r:is_child_of]->(n) 
            WITH n, count(r) AS number 
            ORDER BY number DESC 
            LIMIT 5
            WITH [n.id,number] AS parent 
            UNWIND parent AS parents
            WITH collect(parents) AS result
            MATCH(p:CHECK{id:"taxonomy"}) 
            SET p.big_parents = result
        """
        self.session.run(query,limit=limit)
    
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
    
    def dictionary_to_list(self,dictionary):
        """Convert a dictionary of lists to a list where each key is followed by its value"""
        list_dictionary = []
        for key in dictionary:
            if not dictionary[key]:
                continue
            list_dictionary.append(key)
            list_dictionary.extend(dictionary[key])
        return list_dictionary

    def add_parent_prop_query(self,child,prop_parent,prop_redefined):
        """query the database to add parent related properties"""
        query = """
            MATCH (c)
            WHERE c.id = $child_id
            SET c.stat_parents_prop = $parent_prop
            SET c.stat_parents_redefined_prop = $redefined_prop
        """
        data = {"child_id":child["id"]}
        data["parent_prop"] = self.dictionary_to_list(prop_parent)
        data["redefined_prop"] = self.dictionary_to_list(prop_redefined)
        self.session.run(query,data)

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
            child,parents = result.values()
            prop_parents={}
            prop_redefined={}
            for parent in parents:
                id = parent["id"]
                prop_parents[id] = []
                prop_redefined[id] = []
                for property in parent:
                    if property.startswith('prop_'):
                        if property in child:
                            prop_redefined[id].append(property)
                        else:
                            prop_parents[id].append(property)
            self.add_parent_prop_query(child,prop_parents,prop_redefined)

    def add_child_stat_query(self,parent,prop_redefined,number,missing_lc):
        """query the database to add child related properties"""
        query = """
            MATCH (p)
            WHERE p.id = $parent_id
            SET p.stat_children_redefined_prop = $redefined_prop
            SET p.stat_children_using_synonyms = $number
            SET p.stat_missing_translation = $missing_lc
        """
        data = {"parent_id":parent["id"]}
        data["redefined_prop"] = self.dictionary_to_list(prop_redefined)
        data["number"] = number
        data["missing_lc"] = self.dictionary_to_list(missing_lc)
        self.session.run(query,data)

    def list_tags_lc(self,node):
        """return a list of language codes (lc) used in the node tags"""
        lc_list=[]
        for property in node:
            if property.startswith('tags_ids_'):
                lc_list.append(property.split("_",2)[2])
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
            children,parent = result.values()
            using_synonyms = 0
            prop_redefined={}
            parent_lc = self.list_tags_lc(parent)
            missing_lc = {}
            for child in children:
                if parent["id"] not in child["parents"]:
                    using_synonyms += 1
                id = child["id"]
                prop_redefined[id] = []
                for property in child:
                    if property.startswith('prop_'):
                        if property in parent:
                            prop_redefined[id].append(property)
                    elif property.startswith('tags_ids_'):
                        child_lc = property.split("_",2)[2]
                        if child_lc not in parent_lc:
                            if child_lc not in missing_lc:
                                missing_lc[child_lc] = [child["id"]]
                            else:
                                missing_lc[child_lc].append(child["id"])
            self.add_child_stat_query(parent,prop_redefined,using_synonyms,missing_lc)

    def check_language(self,threshold=3):
        """Add nodes with the percentage of translation in each language"""
        query = "MATCH (n:ENTRY) RETURN n"
        results = self.session.run(query)

        #dictionary used to track the number of translated nodes for each language
        language={}
        #total number of nodes
        number_of_nodes = 0 
        #number of nodes with at least 3 translations
        nodes_with_3translations = 0 
        #list of nodes (their id) with less than 3 translations
        nodes_missing_translation =[]

        # Counting
        for result in results:
            number_of_nodes += 1
            node = result.value()
            number_of_translation = 0
            for property in node:
                if property.startswith('tags_ids_'):
                    number_of_translation += 1
                    lc = property.split('_',2)[2]
                    if lc in language:
                        language[lc] += 1
                    else:
                        language[lc] = 1
            if number_of_translation < threshold:
                nodes_missing_translation.append(node["id"])
            else:
                nodes_with_3translations += 1

        percentage_translated = nodes_with_3translations / number_of_nodes * 100
        language = {k : v / number_of_nodes * 100 for k,v in language.items()}

        # Adding the result in the database
        # First the main language node with general information
        query = """
            CREATE (main:CHECK {id : '__language__'})
            SET main.nodes_missing_translation = $list
            SET main.percentage_with_3_translations_or_more = $percentage
        """
        self.session.run(query,list=nodes_missing_translation,percentage=percentage_translated)
        # Then all the sub-nodes for every language with their percentage
        for lc in language:
            query = "CREATE (n:CHECK{id:'" + lc + "',percentage: $" + lc + "}) \n"
            self.session.run(query,language)
        query = """
            MATCH(main:CHECK {id : '__language__'})
            MATCH(n:CHECK)
            CREATE (n)-[:from]->(main)
        """
        self.session.run(query)

    def tags_use_synonyms(self,tags,synonyms):
        """check if a list of tags contains one or more synonyms and count them"""
        synonyms_use_count = [0 for i in range(len(synonyms))]
        for tag in tags:
            for i,group in enumerate(synonyms):
                for synonym in group:
                    if synonym in tag:
                        synonyms_use_count[i]+=1
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
                    lc = property.split('_',2)[2]
                    if synonyms.get(lc):
                        synonyms[lc].append(node[property])
                        counter_synonyms_use[lc].append([0,0])
                    else:
                        synonyms[lc] = [node[property]]
                        counter_synonyms_use[lc] = [[0,0]]

        # check if synonyms are used
        query = "MATCH (n:ENTRY) return n"
        results = self.session.run(query)
        for result in results:
            node = result.value()
            for property in node:
                if property.startswith("tags_ids_"):
                    lc = property.split('_',2)[2]
                    if lc in synonyms:
                        tags = node[property]
                        add = self.tags_use_synonyms(tags,synonyms[lc])
                        for i in range(len(counter_synonyms_use[lc])):
                            if add[i]:
                                counter_synonyms_use[lc][i][0] += add[i]
                                counter_synonyms_use[lc][i][1] += 1

        # add the data on synonyms usage to their respective node
        for lc in synonyms:
            for i,synonym in enumerate(synonyms[lc]):
                query = f""" MATCH(n:SYNONYMS) 
                    WHERE n.tags_ids_{lc} = $synonym
                    SET n.used_total = $total
                    SET n.used_in_different_entries = $entries
                """
                data = {"synonym":synonym}
                data["total"] = counter_synonyms_use[lc][i][0]
                data["entries"] = counter_synonyms_use[lc][i][1]
                self.session.run(query,data)

if __name__ == "__main__":
    use = Parser()
    use("test")
