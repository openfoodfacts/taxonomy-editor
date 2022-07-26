"""
Taxonomy Editor Backend API
"""
# Required imports
#------------------------------------------------------------------------#
from datetime import datetime

# FastAPI
from fastapi import FastAPI, status, Response, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Data model imports
from .models import Header, Footer

# DB helper imports
from .entries import initialize_db, shutdown_db
from .entries import get_all_nodes, get_nodes
from .entries import update_nodes
#------------------------------------------------------------------------#

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
    Initialize database
    """
    initialize_db()

@app.on_event("shutdown")
async def shutdown():
    """
    Shutdown database
    """
    shutdown_db()

# Helper methods

def check_single(id):
    """
    Helper function for checking whether there is only a single entry with given id
    """
    if len(id) == 0:
        raise HTTPException(status_code=404, detail="Entry not found")
    elif len(id) > 1:
        raise HTTPException(status_code=500, detail="Multiple entries found")

# Get methods

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

@app.get("/nodesfull")
async def findAllNodes(response: Response):
    """
    Get all nodes within taxonomy
    """
    result = get_all_nodes("")
    allNodes = list(result)
    return allNodes

@app.get("/entry/{entry}")
async def findOneEntry(response: Response, entry: str):
    """
    Get entry corresponding to id within taxonomy
    """
    result = get_nodes("ENTRY", entry)
    oneEntry = list(result)

    check_single(oneEntry)
    
    return oneEntry[0]

@app.get("/entriesfull")
async def findAllEntries(response: Response):
    """
    Get all entries within taxonomy
    """
    result = get_all_nodes("ENTRY")
    allEntries = list(result)
    return allEntries

@app.get("/synonym/{synonym}")
async def findOneSynonym(response: Response, synonym: str):
    """
    Get synonym corresponding to id within taxonomy
    """
    result = get_nodes("SYNONYMS", synonym)
    oneSynonym = list(result)

    check_single(oneSynonym)

    return oneSynonym[0]

@app.get("/synonymsfull")
async def findAllSynonyms(response: Response):
    """
    Get all synonyms within taxonomy
    """
    result = get_all_nodes("SYNONYMS")
    allSyononyms = list(result)
    return allSyononyms

@app.get("/stopword/{stopword}")
async def findOneStopword(response: Response, stopword: str):
    """
    Get stopword corresponding to id within taxonomy
    """
    result = get_nodes("STOPWORDS", stopword)
    oneStopword = list(result)
    
    check_single(oneStopword)

    return oneStopword[0]

@app.get("/stopwordsfull")
async def findAllStopwords(response: Response):
    """
    Get all stopwords within taxonomy
    """
    result = get_all_nodes("STOPWORDS")
    allStopwords = list(result)
    return allStopwords

@app.get("/header")
async def findHeader(response: Response):
    """
    Get __header__ within taxonomy
    """
    result = get_nodes("TEXT", "__header__")
    header = list(result)
    return header[0]

@app.get("/footer")
async def findFooter(response: Response):
    """
    Get __footer__ within taxonomy
    """
    result = get_nodes("TEXT", "__footer__")
    footer = list(result)
    return footer[0]

# Post methods

@app.post("/edit/entry/{entry}")
async def editEntry(request: Request, entry: str):
    """
    Editing an entry in a taxonomy.
    New key-value pairs can be added, old key-value pairs can be updated.
    URL will be of format '/edit/<id>'
    """
    incomingData = await request.json()
    result = update_nodes("ENTRY", entry, incomingData)
    updatedEntry = list(result)
    return updatedEntry

@app.post("/edit/synonym/{synonym}")
async def editSynonyms(request: Request, synonym: str):
    """
    Editing a synonym in a taxonomy.
    New key-value pairs can be added, old key-value pairs can be updated.
    URL will be of format '/edit/synonym/<id>'
    """
    incomingData = await request.json()
    result = update_nodes("SYNONYMS", synonym, incomingData)
    updatedSynonym = list(result)
    return updatedSynonym

@app.post("/edit/stopword/{stopword}")
async def editStopwords(request: Request, stopword: str):
    """
    Editing a stopword in a taxonomy.
    New key-value pairs can be added, old key-value pairs can be updated.
    URL will be of format '/edit/stopword/<id>'
    """
    incomingData = await request.json()
    result = update_nodes("STOPWORDS", stopword, incomingData)
    updatedStopword = list(result)
    return updatedStopword

@app.post("/edit/header")
async def editHeader(incomingData: Header):
    """
    Editing the __header__ in a taxonomy.
    """
    convertedData = incomingData.dict()
    result = update_nodes("TEXT", "__header__", convertedData)
    updatedHeader = list(result)
    return updatedHeader

@app.post("/edit/footer")
async def editFooter(incomingData: Footer):
    """
    Editing the __footer__ in a taxonomy.
    """
    convertedData = incomingData.dict()
    result = update_nodes("TEXT", "__footer__", convertedData)
    updatedFooter = list(result)
    return updatedFooter