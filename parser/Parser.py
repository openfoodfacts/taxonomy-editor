from neo4j import GraphDatabase
import re,unicodedata,unidecode


class Parser:

    def __init__(self,filename,uri="bolt://localhost:7687"):
        self.driver = GraphDatabase.driver(uri)
        self.session = self.driver.session()
        self.filename=filename

    def openfile(self):
        """open the file filename and return the list of entries, each entry is a list a the sanitized lines"""
        name = self.filename + ( '.txt' if (len(self.filename)<4 or self.filename[-4:]!=".txt") else '')  #to not get error if extension is missing
        txtfile=open(name,"r",encoding='utf8')
        self.file = txtfile.readlines()

    def file_iter(self,start=0):
        """generator to get the file line by line"""
        for line in self.file[start:] :
            # sanitizing
            line = line.rstrip()
            line = line.replace("’", "'")
            line = re.sub(r"(\d),(\d)", r"\1‚\2", line)
            line = re.sub(r"\\,", "\\‚", line)
            line = re.sub(r"\(([ivx]+)\)", r"\1", line, flags=re.I)
            yield line

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
        if len(line)<=3:return line
        else:
            lang=line[:2]
            new_line=lang+":"
            for word in line[3:].split(","):
                new_line+=self.normalizing(word,lang)+','
            new_line=new_line[:-1]
            return new_line

    def create_headernode(self,header):
        query="CREATE (node{id:'__header__'" + (",value:'"+header if len(header)>0 else "") +"'})"
        self.session.run(query)

    def create_stopwords_synonyms_node(self,id,value,block_index,comment=[],block_subindex=0):
        id_query = " CREATE (n{id:'" + id + "'}) SET n.block_index=" + str(block_index) + ", n.block_subindex="+str(block_subindex)+", n.preceding_lines="+str(comment)
        value_query = " SET n.value='" + str(value) + "'"
        query=id_query+value_query
        # print(query)
        self.session.run(query)

    def create_entry_node(self,id,tags,tagsid,block_index,properties=[],parent_tag=[],comment=[],block_subindex=0):
        id_query = " CREATE (n{id:'" + id + "'}) SET n.block_index=" + str(block_index) + ", n.block_subindex="+str(block_subindex)+", n.preceding_lines="+str(comment)
        entry_query = " SET n.tags=\"" + str(tags) + "\" ,n.tagsid=" + str(tagsid) + " ,n.parents=" + str(parent_tag) + " ,n.properties=" + str(properties)
        query=id_query+entry_query
        # print(query)
        self.session.run(query)

    def harvest(self):
        """Transform data in file to nodes in with neo4j"""
        index_comm=0
        index_stopwords=1
        index_synonyms=1
        language_code_prefix = re.compile('[a-zA-Z][a-zA-Z]:')

        #header
        h=0
        header=''
        for line in self.file_iter():
            if len(line)>0 :
                if line[0]=='#':
                    header+=line
                else : break
            h+=1
        self.create_headernode(header)

        #the other entries
        block_index = 1 #to count block
        end_entry = False
        id=''
        comment=[]
        parent_tag=[]
        tags={}
        tagsid=[]
        properties=[]
        value=''
        for line in self.file_iter(h):

            if line == '':
                if id or tags or tagsid or properties or value or comment: #allows nodes of comment only
                    end_entry = True
            elif line[0]=="#":
                index_comm+=1
                comment.append(self.normalizing(line))
            elif 'stopword' in line:
                id = "stopwords:"+str(index_stopwords)
                index_stopwords+=1
                value = self.normalizing(line[10:])
            elif 'synonym' in line:
                id = "synonyms:"+str(index_synonyms)
                value = self.normalizing(line[9:])
            elif line[0]=="<":
                parent_tag.append(self.normalizing(line[1:]))
            elif language_code_prefix.match(line):
                if not id : id=self.add_line(line.split(',')[0])
                #add tags and tagsid
                lang=line[:2]
                tags_list=[]
                for word in line[3:].split(','):
                    word_normalized=self.normalizing(word,lang)
                    tags_list.append(word_normalized)
                    tagsid.append(lang+':'+word_normalized)
                tags[lang]=tags_list
            else:
                property_name, property_value = self.normalizing(line[:line.index(":")],"en"),add_line(line[line.index(":")+1:])
                property={"id":len(properties)+1,"name":property_name,"value":property_value}
                properties.append(str(property))

            #adding the node to database
            if end_entry:
                if value : self.create_stopwords_synonyms_node(id,value,block_index,comment)
                else : self.create_entry_node(id,tags,tagsid,block_index,properties,parent_tag,comment)

                #reinitialize
                block_index+=1
                end_entry = False
                id=''
                comment=[]
                parent_tag=[]
                tags={}
                tagsid=[]
                properties=[]
                value=''
    def create_child_link(self,parent_id,child_id):
        query="MATCH(p) WHERE '" + parent_id + "' IN p.tagsid" + " match(c) WHERE c.id='" + child_id + "' CREATE (c)-[:is_child_of]->(p)"
        # print(query)
        self.session.run(query)

    def parent(self):
        """Create the relations between nodes"""
        query = "match(n) WHERE size(n.parents)>0 return n.id, n.parents"
        results = self.session.run(query)
        for result in results:
            id=result["n.id"]
            parent_list=result["n.parents"]
            for parent in parent_list:
                self.create_child_link(parent,id)


if __name__ == "__main__":
    use=Parser("test")
    use.openfile()
    use.harvest()
    use.parent()