"""
Taxonomy Editor Backend API
"""
# Required imports
#---------------------------------------------------------------------------------------#
from datetime import datetime

# FastAPI
from fastapi import FastAPI, status, Response, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Data model imports
from .models import Header, Footer

# DB helper imports
from . import graph_db
from .entries import get_all_nodes, get_nodes, get_children, get_parents, get_label
from .entries import full_text_search
from .entries import update_nodes, update_node_children
from .entries import create_node, add_node_to_end, add_node_to_beginning, delete_node
#---------------------------------------------------------------------------------------#

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
    graph_db.initialize_db()

@app.on_event("shutdown")
async def shutdown():
    """
    Shutdown database
    """
    graph_db.shutdown_db()

@app.middleware("http")
async def initialize_neo4j_transactions(request: Request, call_next):
    with graph_db.TransactionCtx():
        response = await call_next(request)
    return response

# Helper methods

def check_single(id):
    """
    Helper function for checking whether there is only a single entry with given id
    """
    if len(id) == 0:
        raise HTTPException(status_code=404, detail="Entry not found")
    elif len(id) > 1:
        raise HTTPException(status_code=500, detail="Multiple entries found")

def get_multi_label(branch, taxonomy):
    return ('t_'+taxonomy)+':'+('b_'+branch)

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

@app.get("/{taxonomy}/{branch}/nodes")
async def findAllNodes(response: Response, branch: str, taxonomy: str):
    """
    Get all nodes within taxonomy
    """
    result = get_all_nodes("", get_multi_label(branch, taxonomy))
    allNodes = list(result)
    return allNodes

@app.get("/{taxonomy}/{branch}/entry/{entry}")
async def findOneEntry(response: Response, branch: str, taxonomy: str, entry: str):
    """
    Get entry corresponding to id within taxonomy
    """
    result = get_nodes("ENTRY", entry, get_multi_label(branch, taxonomy))
    oneEntry = list(result)

    check_single(oneEntry)
    
    return oneEntry[0]

@app.get("/{taxonomy}/{branch}/entry/{entry}/parents")
async def findOneEntryParents(response: Response, branch: str, taxonomy: str, entry: str):
    """
    Get parents for a entry corresponding to id within taxonomy
    """
    result = get_parents(entry, get_multi_label(branch, taxonomy))
    oneEntryParents = list(result)
    
    return oneEntryParents

@app.get("/{taxonomy}/{branch}/entry/{entry}/children")
async def findOneEntryChildren(response: Response, branch: str, taxonomy: str, entry: str):
    """
    Get children for a entry corresponding to id within taxonomy
    """
    result = get_children(entry, get_multi_label(branch, taxonomy))
    oneEntryChildren = list(result)
    
    return oneEntryChildren

@app.get("/{taxonomy}/{branch}/entry")
async def findAllEntries(response: Response, branch: str, taxonomy: str):
    """
    Get all entries within taxonomy
    """
    result = get_all_nodes("ENTRY", get_multi_label(branch, taxonomy))
    allEntries = list(result)
    return allEntries

@app.get("/{taxonomy}/{branch}/synonym/{synonym}")
async def findOneSynonym(response: Response, branch: str, taxonomy: str, synonym: str):
    """
    Get synonym corresponding to id within taxonomy
    """
    result = get_nodes("SYNONYMS", synonym, get_multi_label(branch, taxonomy))
    oneSynonym = list(result)

    check_single(oneSynonym)

    return oneSynonym[0]

@app.get("/{taxonomy}/{branch}/synonym")
async def findAllSynonyms(response: Response, branch: str, taxonomy: str):
    """
    Get all synonyms within taxonomy
    """
    result = get_all_nodes("SYNONYMS", get_multi_label(branch, taxonomy))
    allSyononyms = list(result)
    return allSyononyms

@app.get("/{taxonomy}/{branch}/stopword/{stopword}")
async def findOneStopword(response: Response, branch: str, taxonomy: str, stopword: str):
    """
    Get stopword corresponding to id within taxonomy
    """
    result = get_nodes("STOPWORDS", stopword, get_multi_label(branch, taxonomy))
    oneStopword = list(result)
    
    check_single(oneStopword)

    return oneStopword[0]

@app.get("/{taxonomy}/{branch}/stopword")
async def findAllStopwords(response: Response, branch: str, taxonomy: str):
    """
    Get all stopwords within taxonomy
    """
    result = get_all_nodes("STOPWORDS", get_multi_label(branch, taxonomy))
    allStopwords = list(result)
    return allStopwords

@app.get("/{taxonomy}/{branch}/header")
async def findHeader(response: Response, branch: str, taxonomy: str):
    """
    Get __header__ within taxonomy
    """
    result = get_nodes("TEXT", "__header__", get_multi_label(branch, taxonomy))
    header = list(result)
    return header[0]

@app.get("/{taxonomy}/{branch}/footer")
async def findFooter(response: Response, branch: str, taxonomy: str):
    """
    Get __footer__ within taxonomy
    """
    result = get_nodes("TEXT", "__footer__", get_multi_label(branch, taxonomy))
    footer = list(result)
    return footer[0]

@app.get("/{taxonomy}/{branch}/search")
async def searchNode(response: Response, branch: str, taxonomy: str, query: str):
    result = full_text_search(query, branch, taxonomy)
    return result

# Post methods

@app.post("/{taxonomy}/{branch}/nodes")
async def createNode(request: Request, branch: str, taxonomy: str):
    """
    Creating a new node in a taxonomy
    """
    incomingData = await request.json()
    id = incomingData["id"]
    main_language = incomingData["main_language"]
    if (id == None):
        raise HTTPException(status_code=400, detail="Invalid id")
    if (main_language == None):
        raise HTTPException(status_code=400, detail="Invalid main language code")

    create_node(get_label(id), id, main_language, get_multi_label(branch, taxonomy))
    if (get_label(id) == "ENTRY"):
        add_node_to_end(get_label(id), id, get_multi_label(branch, taxonomy))
    else:
        add_node_to_beginning(get_label(id), id, get_multi_label(branch, taxonomy))

@app.post("/{taxonomy}/{branch}/entry/{entry}")
async def editEntry(request: Request, branch: str, taxonomy: str, entry: str):
    """
    Editing an entry in a taxonomy.
    New key-value pairs can be added, old key-value pairs can be updated.
    URL will be of format '/entry/<id>'
    """
    incomingData = await request.json()
    result = update_nodes("ENTRY", entry, incomingData, get_multi_label(branch, taxonomy))
    updatedEntry = list(result)
    return updatedEntry

@app.post("/{taxonomy}/{branch}/entry/{entry}/children")
async def editEntryChildren(request: Request, branch: str, taxonomy: str, entry: str):
    """
    Editing an entry's children in a taxonomy.
    New children can be added, old children can be removed.
    URL will be of format '/entry/<id>/children'
    """
    incomingData = await request.json()
    result = update_node_children(entry, incomingData, get_multi_label(branch, taxonomy))
    updatedChildren = list(result)
    return updatedChildren

@app.post("/{taxonomy}/{branch}/synonym/{synonym}")
async def editSynonyms(request: Request, branch: str, taxonomy: str, synonym: str):
    """
    Editing a synonym in a taxonomy.
    New key-value pairs can be added, old key-value pairs can be updated.
    URL will be of format '/synonym/<id>'
    """
    incomingData = await request.json()
    result = update_nodes("SYNONYMS", synonym, incomingData, get_multi_label(branch, taxonomy))
    updatedSynonym = list(result)
    return updatedSynonym

@app.post("/{taxonomy}/{branch}/stopword/{stopword}")
async def editStopwords(request: Request, branch: str, taxonomy: str, stopword: str):
    """
    Editing a stopword in a taxonomy.
    New key-value pairs can be added, old key-value pairs can be updated.
    URL will be of format '/stopword/<id>'
    """
    incomingData = await request.json()
    result = update_nodes("STOPWORDS", stopword, incomingData, get_multi_label(branch, taxonomy))
    updatedStopword = list(result)
    return updatedStopword

@app.post("/{taxonomy}/{branch}/header")
async def editHeader(incomingData: Header, branch: str, taxonomy: str):
    """
    Editing the __header__ in a taxonomy.
    """
    convertedData = incomingData.dict()
    result = update_nodes("TEXT", "__header__", convertedData, get_multi_label(branch, taxonomy))
    updatedHeader = list(result)
    return updatedHeader

@app.post("/{taxonomy}/{branch}/footer")
async def editFooter(incomingData: Footer, branch: str, taxonomy: str):
    """
    Editing the __footer__ in a taxonomy.
    """
    convertedData = incomingData.dict()
    result = update_nodes("TEXT", "__footer__", convertedData, get_multi_label(branch, taxonomy))
    updatedFooter = list(result)
    return updatedFooter

# Delete methods

@app.delete("/{taxonomy}/{branch}/nodes")
async def deleteNode(request: Request, branch: str, taxonomy: str):
    """
    Deleting given node from a taxonomy
    """
    incomingData = await request.json()
    id = incomingData["id"]
    delete_node(get_label(id), id, get_multi_label(branch, taxonomy))