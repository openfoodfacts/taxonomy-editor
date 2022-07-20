from neo4j import GraphDatabase
import re,unicodedata,unidecode


class Parser:

    def __init__(self,uri="bolt://localhost:7687"):
        self.driver = GraphDatabase.driver(uri)
        self.session = self.driver.session() #Doesn't create error even if there is no active database

    def normalized_filename(self,filename):
        """ add the .txt extension if it is missing in the filename """
        return filename + ( '.txt' if (len(filename)<4 or filename[-4:]!=".txt") else '')
    
    def file_iter(self,filename,start=0):
        """generator to get the file line by line"""
        counter=0
        with open(filename,"r",encoding="utf8") as file:
            for line_number,line in enumerate(file):
                if line_number < start :
                    continue
                # sanitizing
                #remove any space characters at end of line
                line = line.rstrip()
                #replace ’ (typographique quote) to simple quote '
                line = line.replace("’", "'")
                #replace commas that have no space around by a lower comma character and do the same for escaped comma (preceded by a \) (to distinguish them from commas acting as tags separators)
                line = re.sub(r"(\d),(\d)", r"\1‚\2", line)
                line = re.sub(r"\\,", "\\‚", line)
                #removes parenthesis for roman numeral
                line = re.sub(r"\(([ivx]+)\)", r"\1", line, flags=re.I)
                yield line_number,line
        yield 0,"" #to end the last entry if not ended, line number useless

    def normalizing(self,line,lang="default"):
        """normalize a string depending of the language code lang"""
        line = unicodedata.normalize("NFC", line)
        if lang in ['fr','ca','es','it','nl','pt','sk','en']: #removing accent
            line = unidecode.unidecode(line)
        if lang not in [ ]: #lower case except if language in list
            line=line.lower()
        line = re.sub(r"[\u0000-\u0027\u200b]", "-", line)
        line = re.sub(r"&\w+;", "-", line)
        line = re.sub(r"[\s!\"#\$%&'()*+,\/:;<=>?@\[\\\]^_`{\|}~¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿×ˆ˜–—‘’‚“”„†‡•…‰‹›€™\t]", "-", line)
        line = re.sub(r"-+", "-", line)
        line = line.strip("-")
        return line


    def add_line(self,line):
        """to get a normalized string but keeping the language code "lc:" and the "," separators"""
        if len(line)<=3:return self.normalizing(line)
        else:
            lang=line[:2]
            new_line=lang+":"
            for word in line[3:].split(","):
                new_line+=self.normalizing(word,lang)+','
            new_line=new_line[:-1]
            return new_line

    def create_headernode(self,header):
        """ create the node for the header """
        query="CREATE (node{id:'__header__'})"
        if header :
            query += "SET node.value= $header"
        self.session.run(query,header=header)

    def create_node(self,data):
        """ run the query to create the node with data dictionary """
        id_query = """
            CREATE (n{id: $id })
            SET n.block_index = $block_index
            SET n.block_subindex = 0
            SET n.preceding_lines= $comment
            SET n.src_position= $src_position
        """
        if data['value'] : entry_query = " SET n.value= $value "
        else : entry_query = " SET n.tags= $tags, n.tagsid= $tagsid, n.parents= $parent_tag, n.properties= $properties "
        query=id_query+entry_query
        data["tags"]=str(data["tags"]) #can't add dictionary in database... I think
        self.session.run(query,data,block_index=self.block_index,)

    def new_node_data(self):
        """ To create an empty dictionary that will be used to create node """
        data = {
                "id" : '',
                "comment" : [],
                "parent_tag" : [],
                "tags" : {},
                "tagsid" : [],
                "properties" : [],
                "value" : '',
                'src_position' : 0,
        }
        return data

    def set_data_id(self,data,id,line_number):
        if not data['id'] :
            data['id']=id
        else :
            message = "Trying to overwrite an entry due to a missing new line at line " + str(line_number)
            raise Warning(message)
        return data

    def header_harvest(self,filename):
        """ to harvest the header (comment with #), it has its own function because some header has multiple blocks """
        h=0
        header=[]
        for _,line in self.file_iter(filename):
            if line :
                if line[0]=='#':
                    header.append(self.normalizing(line[1:]))
                else : break
            h+=1
        return header,h

    def harvest(self,filename):
        """Transform data from file to dictionary"""
        index_comm=0
        index_stopwords=1
        index_synonyms=1
        language_code_prefix = re.compile('[a-zA-Z][a-zA-Z]:')

        #header
        header,next_line = self.header_harvest()
        yield header

        #the other entries
        self.block_index = 1 #to count block
        data = self.new_node_data()
        for line_number,line in self.file_iter(filename,next_line):

            if line == '': # can be the end of an block or just 2 line separators, file_iter() always end with ''
                if data['id']: # to be sure that it's an entry block end
                    yield data #another function will use this dictionary to create a node
                    data = self.new_node_data()
                    self.block_index+=1
            else :
                if not data['src_position'] : data['src_position'] = line_number + 1
                if line[0]=="#":
                    index_comm+=1
                    data['comment'].append(self.normalizing(line,"en"))
                elif 'stopword' in line:
                    id = "stopwords:"+str(index_stopwords)
                    data=self.set_data_id(data,id,line_number)
                    index_stopwords+=1
                    data['value'] = self.add_line(line[10:])
                elif 'synonym' in line:
                    id = "synonyms:"+str(index_synonyms)
                    data=self.set_data_id(data,id,line_number)
                    index_synonyms+=1
                    data['value'] = self.add_line(line[9:])
                elif line[0]=="<":
                    data['parent_tag'].append(self.add_line(line[1:]))
                elif language_code_prefix.match(line):
                    if not data['id'] : data['id']=self.add_line(line.split(',',1)[0])
                    #add tags and tagsid
                    lang=line[:2]
                    tags_list=[]
                    for word in line[3:].split(','):
                        word_normalized=self.normalizing(word,lang)
                        tags_list.append(word_normalized)
                        data['tagsid'].append(lang+':'+word_normalized)
                    data['tags'][lang]=tags_list
                else:
                    property_name = self.normalizing(line[:line.index(":")],"en")
                    property_value = self.add_line(line[line.index(":")+1:])
                    propery_id = len(data['properties'])+1
                    property = {"id":propery_id , "name":property_name , "value":property_value}
                    data['properties'].append(str(property))

    def create_nodes(self,filename):
        """Adding nodes to database"""
        filename = self.normalized_filename(filename)
        harvested_data = self.harvest(filename)
        self.create_headernode(next(harvested_data))
        for entry in harvested_data:
            self.create_node(entry)

    def parent_search(self):
        """Get the parent and the child to link"""
        query = "match(n) WHERE size(n.parents)>0 return n.id, n.parents"
        results = self.session.run(query)
        for result in results:
            id=result["n.id"]
            parent_list=result["n.parents"]
            for parent in parent_list:
                yield parent,id

    def create_child_link(self):
        """Create the relations between nodes"""
        for parent_id,child_id in self.parent_search():
            query="""
                MATCH(p) WHERE $parent_id IN p.tagsid
                MATCH(c) WHERE c.id= $child_id
                CREATE (c)-[:is_child_of]->(p)
            """
            self.session.run(query , parent_id=parent_id , child_id=child_id)

    def __call__(self,filename):
        """ process the file """
        self.create_nodes(filename)
        self.create_child_link()

if __name__ == "__main__":
    use=Parser()
    use("test")