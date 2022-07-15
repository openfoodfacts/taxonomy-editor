from neo4j import GraphDatabase
import re,unicodedata,unidecode


class Parser:

    def __init__(self,filename,uri="bolt://localhost:7687"):
        self.driver = GraphDatabase.driver(uri)
        self.session = self.driver.session() #Doesn't create error even if there is no active database
        self.filename=filename

    def file_name(self):
        """open the file filename and return the list of entries, each entry is a list a the sanitized lines"""
        self.filename = self.filename + ( '.txt' if (len(self.filename)<4 or self.filename[-4:]!=".txt") else '')  #to not get error if extension is missing

    def file_iter(self,start=0):
        """generator to get the file line by line"""
        counter=0
        with open(self.filename,"r",encoding="utf8") as file:
            for line in file:
                if counter < start : counter+=1
                else :
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
                    yield line
        yield "" #to end the last entry if not ended

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
        query="CREATE (node{id:'__header__'" + (",value:'"+ header + "'" if header else "") +"})"
        self.session.run(query)

    def create_node(self,data):
        id_query = " CREATE (n{id:'" + data['id'] + "'}) SET n.block_index=" + str(self.block_index) + ", n.block_subindex=0, n.preceding_lines="+str(data['comment'])
        if data['value'] : entry_query = " SET n.value='" + str(data['value']) + "'"
        else : entry_query = " SET n.tags=\"" + str(data['tags']) + "\" ,n.tagsid=" + str(data['tagsid']) + " ,n.parents=" + str(data['parent_tag']) + " ,n.properties=" + str(data['properties'])
        query=id_query+entry_query
        # print(query)
        self.session.run(query)

    def reinitialize_data(self):
        data = { "id":'',
        "comment":[],
        "parent_tag":[],
        "tags":{},
        "tagsid":[],
        "properties":[],
        "value":'',
        }
        return data

    def header_harvest(self):
        h=0
        header=''
        for line in self.file_iter():
            if line :
                if line[0]=='#':
                    header+=line
                else : break
            h+=1
        return header,h

    def harvest(self):
        """Transform data in file to nodes in with neo4j"""
        index_comm=0
        index_stopwords=1
        index_synonyms=1
        language_code_prefix = re.compile('[a-zA-Z][a-zA-Z]:')

        #header
        header,next_line = self.header_harvest()
        yield header

        #the other entries
        self.block_index = 1 #to count block
        data = self.reinitialize_data()
        for line in self.file_iter(next_line):

            if line == '':
                if data['id']:
                    yield data
                    data = self.reinitialize_data()
                    self.block_index+=1
            elif line[0]=="#":
                index_comm+=1
                data['comment'].append(self.normalizing(line,"en"))
            elif 'stopword' in line:
                data['id'] = "stopwords:"+str(index_stopwords)
                index_stopwords+=1
                data['value'] = self.add_line(line[10:])
            elif 'synonym' in line:
                data['id'] = "synonyms:"+str(index_synonyms)
                index_synonyms+=1
                data['value'] = self.add_line(line[9:])
            elif line[0]=="<":
                data['parent_tag'].append(self.add_line(line[1:]))
            elif language_code_prefix.match(line):
                if not data['id'] : data['id']=self.add_line(line.split(',')[0])
                #add tags and tagsid
                lang=line[:2]
                tags_list=[]
                for word in line[3:].split(','):
                    word_normalized=self.normalizing(word,lang)
                    tags_list.append(word_normalized)
                    data['tagsid'].append(lang+':'+word_normalized)
                data['tags'][lang]=tags_list
            else:
                property_name, property_value = self.normalizing(line[:line.index(":")],"en"),add_line(line[line.index(":")+1:])
                property={"id":len(data['properties'])+1,"name":property_name,"value":property_value}
                data['properties'].append(str(property))

    def txt2nodes(self):
        """Adding nodes to database"""
        harvested_data = self.harvest()
        self.create_headernode(next(harvested_data))
        for entry in harvested_data:
            self.create_node(entry)

    def parent(self):
        """Create the relations between nodes"""
        query = "match(n) WHERE size(n.parents)>0 return n.id, n.parents"
        results = self.session.run(query)
        for result in results:
            id=result["n.id"]
            parent_list=result["n.parents"]
            for parent in parent_list:
                yield parent,id

    def create_child_link(self):
        for parent_id,child_id in self.parent_search():
            query="MATCH(p) WHERE '" + parent_id + "' IN p.tagsid" + " match(c) WHERE c.id='" + child_id + "' CREATE (c)-[:is_child_of]->(p)"
        self.session.run(query)

    def __call__(self):
        self.file_name()
        self.txt2nodes()
        self.create_child_link()

if __name__ == "__main__":
    use=Parser("test")
    use()