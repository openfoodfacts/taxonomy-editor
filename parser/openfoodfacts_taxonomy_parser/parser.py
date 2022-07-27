from neo4j import GraphDatabase
import re,unicodedata,unidecode
from .exception import DuplicateIDError


class Parser:

    def __init__(self,uri="bolt://localhost:7687"):
        self.driver = GraphDatabase.driver(uri)
        self.session = self.driver.session() #Doesn't create error even if there is no active database

    def create_headernode(self,header):
        """ create the node for the header """
        query = """
                CREATE (n:TEXT {id: '__header__' })
                SET n.preceding_lines= $header
                SET n.src_position= 1
            """
        self.session.run(query,header=header)

    def create_node(self,data):
        """ run the query to create the node with data dictionary """
        position_query = """
            SET n.is_before = $is_before
            SET n.preceding_lines= $comment
            SET n.src_position= $src_position
        """
        entry_query=""
        if data['id'] == '__footer__':
            id_query = " CREATE (n:TEXT {id: $id }) \n "
        elif data['id'].startswith('synonyms'):
            id_query = " CREATE (n:SYNONYMS {id: $id }) \n "
        elif data['id'].startswith('stopwords') :
            id_query = " CREATE (n:STOPWORDS {id: $id }) \n "
        else :
            id_query = " CREATE (n:ENTRY {id: $id , main_language : $main_language}) \n "
            if data['parent_tag'] : entry_query += " SET n.parents = $parent_tag \n"
            for key in data :
                if key.startswith('prop_') :
                    entry_query += " SET n." + key + " = $" + key + '\n'

        for key in data :
            if key.startswith('tags_') :
                entry_query += " SET n." + key + " = $" + key + '\n'

        query = id_query + entry_query + position_query
        self.session.run(query,data,is_before=self.is_before,)

    def normalized_filename(self,filename):
        """ add the .txt extension if it is missing in the filename """
        return filename + ( '.txt' if (len(filename)<4 or filename[-4:]!=".txt") else '')

    def file_iter(self,filename,start=0):
        """generator to get the file line by line"""
        with open(filename,"r",encoding="utf8") as file:
            for line_number,line in enumerate(file):
                if line_number < start :
                    continue
                # sanitizing
                #remove any space characters at end of line
                line = line.rstrip()
                #replace ’ (typographique quote) to simple quote '
                line = line.replace("’", "'")
                # replace commas that have no space around by a lower comma character 
                # and do the same for escaped comma (preceded by a \) 
                # (to distinguish them from commas acting as tags separators)
                line = re.sub(r"(\d),(\d)", r"\1‚\2", line)
                line = re.sub(r"\\,", "\\‚", line)
                #removes parenthesis for roman numeral
                line = re.sub(r"\(([ivx]+)\)", r"\1", line, flags=re.I)
                yield line_number,line
        yield line_number,"" #to end the last entry if not ended

    def normalizing(self,line,lang="default"):
        """normalize a string depending of the language code lang"""
        line = unicodedata.normalize("NFC", line)
        if lang in ['fr','ca','es','it','nl','pt','sk','en']: #removing accent
            line = re.sub(r"[¢£¤¥§©ª®°²³µ¶¹º¼½¾×‰€™]", "-", line)
            line = unidecode.unidecode(line)
        if lang not in [ ]: #lower case except if language in list
            line=line.lower()
        line = re.sub(r"[\u0000-\u0027\u200b]", "-", line)
        line = re.sub(r"&\w+;", "-", line)
        line = re.sub(r"[\s!\"#\$%&'()*+,\/:;<=>?@\[\\\]^_`{\|}~¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿×ˆ˜–—‘’‚“”„†‡•…‰‹›€™\t]", "-", line)
        line = re.sub(r"-+", "-", line)
        line = line.strip("-")
        return line

    def remove_stopwords(self,lc,words):
        """to remove the stopwords that were read at the beginning of the file"""
        if lc in self.stopwords :
            words_to_remove = self.stopwords[lc]
            new_words = []
            for word in words.split("-"):
                if word not in words_to_remove :
                    new_words.append(word)
            return ("-").join(new_words)
        else : return words

    def add_line(self,line):
        """to get a normalized string but keeping the language code "lc:" and the "," (commas) separators , used to add an id to entries and to add a parent tag"""
        if len(line)<=3:return self.normalizing(line)
        else:
            lang=line[:2]
            new_line=lang+":"
            for word in line[3:].split(","):
                new_line+=self.remove_stopwords( lang,self.normalizing(word,lang) ) +','
            new_line=new_line[:-1]
            return new_line

    def get_lc_value(self,line):
        """to get the language code "lc" and a list of normalized values"""
        lc=line[:2]
        new_line=[]
        for word in line[3:].split(","):
            new_line.append( self.remove_stopwords( lc,self.normalizing(word,lc) ) )
        return lc,new_line

    def new_node_data(self):
        """ To create an empty dictionary that will be used to create node """
        data = {
                "id" : '',
                "main_language" : '',
                "comment" : [],
                "parent_tag" : [],
                'src_position' : 0,
        }
        return data

    def set_data_id(self,data,id,line_number):
        if not data['id'] :
            data['id']=id
        else :
            raise DuplicateIDError(line_number)
        return data

    def header_harvest(self,filename):
        """ to harvest the header (comment with #), it has its own function because some header has multiple blocks """
        h=0
        header=[]
        for _,line in self.file_iter(filename):
            if not(line) or line[0]=='#':
                header.append(line)
            else : break
            h+=1

        # we don't want to eat the comments of the next block and it remove the last separating line
        for i in range(len(header)):
            if header.pop():
                h-=1
            else : break

        return header,h

    def harvest(self,filename):
        """Transform data from file to dictionary"""
        index_stopwords=0
        index_synonyms=0
        language_code_prefix = re.compile('[a-zA-Z][a-zA-Z]:')
        self.stopwords=dict()

        #header
        header,next_line = self.header_harvest(filename)
        yield header
        self.is_before = '__header__'

        #the other entries
        data = self.new_node_data()
        for line_number,line in self.file_iter(filename,next_line):
            if line == '': # can be the end of an block or just 2 line separators, file_iter() always end with ''
                if data['id']: # to be sure that the entry block ends
                    yield data #another function will use this dictionary to create a node
                    self.is_before = data['id']
                    data = self.new_node_data()
                else : # there was more than 1 separator line or maybe a comment block before an entry
                    data['comment'].append(line)
            else :
                if line[0]=="#":
                    data['comment'].append(line)
                    if not data['src_position'] : # to get the position of the footer if it's not empty
                        data['src_position'] = line_number + 1
                else :
                    if len(data)==5 and not data['parent_tag'] : # the begining of the entry
                        data['src_position'] = line_number + 1
                    if 'stopword' in line:
                        id = "stopwords:"+str(index_stopwords)
                        data=self.set_data_id(data,id,line_number)
                        index_stopwords+=1
                        lc,value=self.get_lc_value(line[10:])
                        data['tags_' + lc] = value
                        self.stopwords[lc]=value
                    elif 'synonym' in line:
                        id = "synonyms:"+str(index_synonyms)
                        data=self.set_data_id(data,id,line_number)
                        index_synonyms+=1
                        line=line[9:]
                        tags = [words.strip() for words in line[3:].split(",")]
                        lc,value=self.get_lc_value(line)
                        data['tags_' + lc] = tags
                        data['tags_ids_' + lc] = value
                    elif line[0]=="<":
                        data['parent_tag'].append(self.add_line(line[1:]))
                    elif language_code_prefix.match(line):
                        if not data['id'] :
                            data['id']=self.add_line(line.split(',',1)[0])
                            data['main_language']=data['id'][:2] # first 2 characters are language code
                        #add tags and tagsid
                        lang,line=line.split(':',1)
                        tags_list=[]
                        tagsids_list=[]
                        # differenciate separating , from non-separating , by changing separators to " , "
                        line = line.replace(' ,',', ').replace(', ',' , ')
                        for word in line.split(' , '):
                            tags_list.append(word.strip())
                            word_normalized=self.remove_stopwords(lang,self.normalizing(word,lang))
                            tagsids_list.append(word_normalized)
                        data['tags_' + lang] = tags_list
                        data['tags_ids_'+lang]=tagsids_list
                    else:
                        property_name,lc, property_value = line.split(":",2)
                        data['prop_'+ property_name + '_' + lc]= property_value
        data['id'] = '__footer__'
        if not data['src_position'] : data['src_position'] = line_number + 1 # to get position if it's empty
        yield data

    def create_nodes(self,filename):
        """Adding nodes to database"""
        filename = self.normalized_filename(filename)
        harvested_data = self.harvest(filename)
        self.create_headernode(next(harvested_data))
        for entry in harvested_data:
            self.create_node(entry)

    def create_previous_link(self):
        query="MATCH(n) WHERE exists(n.is_before) return n.id,n.is_before"
        results = self.session.run(query)
        for result in results:
            id=result["n.id"]
            id_previous=result['n.is_before']

            query="""
                MATCH(n) WHERE n.id = $id
                MATCH(p) WHERE p.id= $id_previous
                CREATE (p)-[:is_before]->(n)
            """
            self.session.run(query , id=id , id_previous=id_previous)

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
        for parent,child_id in self.parent_search():
            lc,parent_id = parent.split(":")
            tags_ids= "tags_ids_" + lc
            query=""" MATCH(p) WHERE $parent_id IN p.tags_ids_""" + lc
            query += """
                MATCH(c) WHERE c.id= $child_id
                CREATE (c)-[:is_child_of]->(p)
            """
            self.session.run(query , parent_id=parent_id , tagsid=tags_ids , child_id=child_id)

    def delete_used_properties(self):
        query = "MATCH (n) SET n.is_before = null, n.parents = null"
        self.session.run(query)

    def __call__(self,filename):
        """ process the file """
        self.create_nodes(filename)
        self.create_child_link()
        self.create_previous_link()
        # self.delete_used_properties()

if __name__ == "__main__":
    use=Parser()
    use("test")