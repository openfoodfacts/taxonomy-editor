from neo4j import GraphDatabase
import re,unicodedata,unidecode


class Parser:

    def __init__(self,filename,uri="bolt://localhost:7687"):
        self.driver = GraphDatabase.driver(uri)
        self.session = self.driver.session()
        self.filename=filename

    def openfile(self):
        name = self.filename + ( '.txt' if (len(self.filename)<4 or self.filename[-4:]!=".txt") else '')  #to not get error if extension is missing
        txtfile=open(name,"r",encoding='utf8')
        file = [ [ ] ]
        for line in txtfile:
            if line=='\n' and len(file[-1])>0:
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
        '''nonlocal comment'''
        def normalizing(line):
            line = unicodedata.normalize("NFC", line)
            if line[:2] in ['fr','ca','es','it','nl','pt','sk','en']: #removing accent
                line = unidecode.unidecode(line)
            if line[:2] not in [ ]: #lower case except if language in list
                line=line.lower()
            line = re.sub(r"[\u0000-\u0027\u200b]", "-", line)
            line = re.sub(r"&\w+;", "-", line)
            line = re.sub(r"[\s!\"#\$%&'()*+,\/:;<=>?@\[\\\]^_`{\|}~¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿×ˆ˜–—‘’‚“”„†‡•…‰‹›€™\t]", "-", line)
            line = re.sub(r"-+", "-", line)
            line = line.strip("-")
            return line


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
            tags=[]
            properties=[]
            value=''
            id=''

            for line in file[i]:
                print(line)
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
                    else : tags.append(normalizing(line))
                else:
                    property_name, property_value = normalizing(line[:line.index(":")]),normalizing(line[line.index(":")+1:])
                    property={"id":len(properties)+1,}
                    properties.append(str(property))
            print(comment,parent_tag,tags,properties,value,id)


            #adding the node to database
            query="CREATE (n{id:'" + id + ("',value:'"+value+"'" if value else "") + ("',parents:"+str(parent_tag) + ",tags:"+str(tags) + ",properties:"+str(properties) if not value else "")  + ",block_index:"+str(i)+",block_subindex:0,preceding_lines:"+str(comment)+"})"
            print(query)
            self.session.run(query)


if __name__ == "__main__":
    use=Parser("test")
    use.openfile()
    use.harvest()