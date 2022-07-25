from datetime import datetime
from typing import List, Optional
from neo4j import GraphDatabase

# FastAPI
from fastapi import FastAPI, status, Response, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Open Food Facts Taxonomy Editor API")

# Allow anyone to call the API from their own apps
app.add_middleware(
    CORSMiddleware,
    # FastAPI doc related to allow_origin (to avoid CORS issues):
    # "It's also possible to declare the list as "*" (a "wildcard") to say that all are allowed.
    # But that will only allow certain types of communication, excluding everything that involves 
    # credentials: Cookies, Authorization headers like those used with Bearer Tokens, etc.
    # So, for everything to work correctly, it's better to specify explicitly the allowed origins."
    # => Workaround: use allow_origin_regex
    # Source: https://github.com/tiangolo/fastapi/issues/133#issuecomment-646985050
    allow_origin_regex='https?://.*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.on_event("startup")
async def startup():
    """
    Initialize Neo4J database
    """
    global driver, session
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri)
    session = driver.session()

@app.on_event("shutdown")
async def shutdown():
    """
    Close session and driver of Neo4J database
    """
    session.close()
    driver.close()

@app.get("/", status_code=status.HTTP_200_OK)
async def hello():
    return {"message": "Hello user! Tip: open /docs or /redoc for documentation"}

@app.get("/ping")
async def pong(response: Response):
    """
    Check server health
    """
    pong = datetime.now()
    return {"ping": "pong @ %s" % pong}

@app.get("/entry/{entry}")
async def findOneEntry(response: Response, entry: str):
    """
    Get entry corresponding to id within taxonomy
    """
    query = """
        MATCH (n:ENTRY) WHERE n.id = $id 
        RETURN n
    """
    result = session.run(query, {"id": entry})
    oneEntry = [record for record in result]
    return oneEntry

@app.get("/entriesfull")
async def findAllEntries(response: Response):
    """
    Get all entries within taxonomy
    """
    query = """
        MATCH (n:ENTRY) RETURN n
    """
    result = session.run(query)
    allEntries = [record for record in result]
    return allEntries

@app.get("/synonym/{synonym}")
async def findOneSynonym(response: Response, synonym: str):
    """
    Get synonym corresponding to id within taxonomy
    """
    query = """
        MATCH (n:SYNONYMS) WHERE n.id = $id 
        RETURN n
    """
    result = session.run(query, {"id": synonym})
    oneSynonym = [record for record in result]
    return oneSynonym

@app.get("/synonymsfull")
async def findAllSynonyms(response: Response):
    """
    Get all synonyms within taxonomy
    """
    query = """
        MATCH (n:SYNONYMS) RETURN n
    """
    result = session.run(query)
    allSyononyms = [record for record in result]
    return allSyononyms

@app.get("/stopword/{stopword}")
async def findOneStopword(response: Response, stopword: str):
    """
    Get stopword corresponding to id within taxonomy
    """
    query = """
        MATCH (n:STOPWORDS) WHERE n.id = $id 
        RETURN n
    """
    result = session.run(query, {"id": stopword})
    oneStopword = [record for record in result]
    return oneStopword

@app.get("/stopwordsfull")
async def findAllStopwords(response: Response):
    """
    Get all stopwords within taxonomy
    """
    query = """
        MATCH (n:STOPWORDS) RETURN n
    """
    result = session.run(query)
    allStopwords = [record for record in result]
    return allStopwords


@app.get("/header")
async def findHeader(response: Response):
    """
    Get __header__ within taxonomy
    """
    query = """
        MATCH (n:TEXT) WHERE n.id = "__header__"
        RETURN n
    """
    result = session.run(query)
    header = [record for record in result]
    return header

@app.get("/footer")
async def findFooter(response: Response):
    """
    Get __footer__ within taxonomy
    """
    query = """
        MATCH (n:TEXT) WHERE n.id = "__footer__"
        RETURN n
    """
    result = session.run(query)
    footer = [record for record in result]
    return footer

@app.put("/edit/entry/{entry}")
async def editEntry(request: Request, entry: str):
    """
    Editing an entry in a taxonomy.
    New key-value pairs can be added, old key-value pairs can be updated.
    URL will be of format '/edit/<id>'
    """
    incomingData = await request.json()
    result = None
    for key in incomingData.keys():
        query = f"""
            MATCH (n:ENTRY) WHERE n.id = $id
            SET n.{key} = $value
            RETURN n
        """
        result = session.run(query, {"id": entry, "value": incomingData[key]})
    updatedEntry = [record for record in result]
    return updatedEntry

class Header(BaseModel):
    preceding_lines: List

@app.put("/edit/header")
async def editHeader(incomingData: Header):
    """
    Editing the __header__ in a taxonomy.
    """
    convertedData = incomingData.dict()
    query = f"""
        MATCH (n:TEXT) WHERE n.id = "__header__"
        SET n.preceding_lines = {str(convertedData['preceding_lines'])}
        RETURN n
    """
    result = session.run(query)
    updatedHeader = [record for record in result]
    return updatedHeader

class Footer(BaseModel):
    preceding_lines: List

@app.put("/edit/footer")
async def editFooter(incomingData: Footer):
    """
    Editing the __footer__ in a taxonomy.
    """
    convertedData = incomingData.dict()
    query = f"""
        MATCH (n:TEXT) WHERE n.id = "__footer__"
        SET n.preceding_lines = {str(convertedData['preceding_lines'])}
        RETURN n
    """
    result = session.run(query)
    updatedFooter = [record for record in result]
    return updatedFooter