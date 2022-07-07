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
        file = [ [ ] ]
        for line in txtfile:
            if line=='\n' :
                if len(file[-1])>0:
                    file.append([])
            else:
                #sanitizing the line before adding it
                line = line.rstrip()
                line = line.replace("’", "'")
                line = re.sub(r"(\d),(\d)", r"\1‚\2", line)
                line = re.sub(r"\\,", "\\‚", line)
                line = re.sub(r"\(([ivx]+)\)", r"\1", line, flags=re.I)
                file[-1].append(line)
        self.file = file


    def harvest(self):
        """Transform data in file to nodes in with neo4j"""
        def normalizing(line,lang="default"):
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

        def add_line(line):
            """to get a normalized string but keeping the language code "lc:" and the "," separators"""
            if len(line)<=3:return line
            else:
                lang=line[:2]
                new_line=lang+":"
                for word in line[3:].split(","):
                    new_line+=normalizing(word,lang)+','
                new_line=new_line[:-1]
                return new_line

        index_comm=0
        index_stopwords=1
        index_synonyms=1
        stop = re.compile('stopword')
        syno = re.compile('synonym')
        lc = re.compile('[a-zA-Z][a-zA-Z]:')

        #header
        h=0
        header=''
        while self.file[h][0][0]=="#":
            for line in self.file[h]:
                header+=line
            h+=1
        query="CREATE (node{id:'__header__'" + (",value:"+header if len(header)>0 else "") +"})"

        #the other entries
        for i in range(1,len(self.file)) :
            comment=[]
            parent_tag=[]
            tags={}
            tagsid=[]
            properties=[]
            value=''
            id=''

            for line in self.file[i]:
                if line[0]=="#":
                    index_comm+=1
                    comment.append(normalizing(line))
                elif stop.match(line):
                    id = "stopwords:"+str(index_stopwords)
                    value = normalizing(line[10:])
                elif syno.match(line):
                    id = "synonyms:"+str(index_synonyms)
                    value = normalizing(line[9:])
                elif line[0]=="<":
                    parent_tag.append(normalizing(line[1:]))
                elif lc.match(line):
                    if not id : id=normalizing(line)
                    #add tags and tagsid
                    lang=line[:2]
                    tags_list=[]
                    for word in line[3:].split(','):
                        word_normalized=normalizing(word,lang)
                        tags_list.append(word_normalized)
                        tagsid.append(lang+':'+word_normalized)
                    tags[lang]=tags_list
                else:
                    property_name, property_value = normalizing(line[:line.index(":")],"en"),add_line(line[line.index(":")+1:])
                    property={"id":len(properties)+1,"name":property_name,"value":property_value}
                    properties.append(str(property))


            #adding the node to database
            query = "CREATE (n{id:'" + id + ("',value:'"+value+"'" if value else "") + ("',parents:"+str(parent_tag) + ",tags:\""+str(tags) + "\",tagsid:"+str(tagsid)+ ",properties:"+str(properties) if not value else "")  + ",block_index:"+str(i)+",block_subindex:0,preceding_lines:"+str(comment)+"})"
            self.session.run(query)
    
    def parent(self):
        """Create the relations between nodes"""
        query = "match(n) WHERE size(n.parents)>0 return n.id, n.parents"
        results = self.session.run(query)
        for result in results:
            id=result["n.id"]
            parent_list=result["n.parents"]
            for parent in parent_list:
                query="MATCH(p) WHERE '" + parent + "' IN p.tagsid" + " match(c) WHERE c.id='" + id + "' CREATE (c)-[:is_child_of]->(p)"
                self.session.run(query)


if __name__ == "__main__":
    use=Parser("test")
    use.openfile()
    use.harvest()
    use.parent()