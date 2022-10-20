"""
Taxonomy Editor Backend API
"""
# Required imports
#----------------------------------------------------------------------------#
from datetime import datetime

# FastAPI
from fastapi import FastAPI, status, Response, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Data model imports
from .models import Header, Footer

# DB helper imports
from . import graph_db
from .entries import TaxonomyGraph
#----------------------------------------------------------------------------#

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

@app.get("/{taxonomy_name}/{branch}/nodes")
async def findAllNodes(response: Response, branch: str, taxonomy_name: str):
    """
    Get all nodes within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_all_nodes("")
    allNodes = list(result)
    return allNodes

@app.get("/{taxonomy_name}/{branch}/rootnodes")
async def findAllRootNodes(response: Response, branch: str, taxonomy_name: str):
    """
    Get all root nodes within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_all_root_nodes()
    allRootNodes = list(result)
    return allRootNodes

@app.get("/{taxonomy_name}/{branch}/entry/{entry}")
async def findOneEntry(response: Response, branch: str, taxonomy_name: str, entry: str):
    """
    Get entry corresponding to id within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_nodes("ENTRY", entry)
    oneEntry = list(result)

    check_single(oneEntry)
    
    return oneEntry[0]

@app.get("/{taxonomy_name}/{branch}/entry/{entry}/parents")
async def findOneEntryParents(response: Response, branch: str, taxonomy_name: str, entry: str):
    """
    Get parents for a entry corresponding to id within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_parents(entry)
    oneEntryParents = list(result)
    
    return oneEntryParents

@app.get("/{taxonomy_name}/{branch}/entry/{entry}/children")
async def findOneEntryChildren(response: Response, branch: str, taxonomy_name: str, entry: str):
    """
    Get children for a entry corresponding to id within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_children(entry)
    oneEntryChildren = list(result)
    
    return oneEntryChildren

@app.get("/{taxonomy_name}/{branch}/entry")
async def findAllEntries(response: Response, branch: str, taxonomy_name: str):
    """
    Get all entries within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_all_nodes("ENTRY")
    allEntries = list(result)
    return allEntries

@app.get("/{taxonomy_name}/{branch}/synonym/{synonym}")
async def findOneSynonym(response: Response, branch: str, taxonomy_name: str, synonym: str):
    """
    Get synonym corresponding to id within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_nodes("SYNONYMS", synonym)
    oneSynonym = list(result)

    check_single(oneSynonym)

    return oneSynonym[0]

@app.get("/{taxonomy_name}/{branch}/synonym")
async def findAllSynonyms(response: Response, branch: str, taxonomy_name: str):
    """
    Get all synonyms within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_all_nodes("SYNONYMS")
    allSyononyms = list(result)
    return allSyononyms

@app.get("/{taxonomy_name}/{branch}/stopword/{stopword}")
async def findOneStopword(response: Response, branch: str, taxonomy_name: str, stopword: str):
    """
    Get stopword corresponding to id within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_nodes("STOPWORDS", stopword)
    oneStopword = list(result)
    
    check_single(oneStopword)

    return oneStopword[0]

@app.get("/{taxonomy_name}/{branch}/stopword")
async def findAllStopwords(response: Response, branch: str, taxonomy_name: str):
    """
    Get all stopwords within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_all_nodes("STOPWORDS")
    allStopwords = list(result)
    return allStopwords

@app.get("/{taxonomy_name}/{branch}/header")
async def findHeader(response: Response, branch: str, taxonomy_name: str):
    """
    Get __header__ within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_nodes("TEXT", "__header__")
    header = list(result)
    return header[0]

@app.get("/{taxonomy_name}/{branch}/footer")
async def findFooter(response: Response, branch: str, taxonomy_name: str):
    """
    Get __footer__ within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_nodes("TEXT", "__footer__")
    footer = list(result)
    return footer[0]

@app.get("/{taxonomy_name}/{branch}/search")
async def searchNode(response: Response, branch: str, taxonomy_name: str, query: str):
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.full_text_search(query)
    return result

@app.get("/{taxonomy_name}/{branch}/export")
async def exportToTextFile(response: Response, branch: str, taxonomy_name: str):
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.export_taxonomy()
    return FileResponse(result)

# Post methods

@app.post("/{taxonomy_name}/{branch}/import")
async def importFromGithub(request: Request, branch: str, taxonomy_name: str):
    """
    Get taxonomy from Product Opener GitHub repository 
    """
    incomingData = await request.json()
    description = incomingData["description"]

    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    if (not taxonomy.is_valid_branch_name()):
        raise HTTPException(status_code=500, detail="Enter a valid branch name!")
    if (taxonomy.does_project_exist()):
        raise HTTPException(status_code=500, detail="Project already exists!")
    if (taxonomy.is_branch_unique()):
        raise HTTPException(status_code=500, detail="Branch name should be unique!")

    result = taxonomy.import_from_github(description)
    return result

@app.post("/{taxonomy_name}/{branch}/nodes")
async def createNode(request: Request, branch: str, taxonomy_name: str):
    """
    Creating a new node in a taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    incomingData = await request.json()
    id = incomingData["id"]
    main_language = incomingData["main_language"]
    if (id == None):
        raise HTTPException(status_code=400, detail="Invalid id")
    if (main_language == None):
        raise HTTPException(status_code=400, detail="Invalid main language code")

    taxonomy.create_node(taxonomy.get_label(id), id, main_language)
    if (taxonomy.get_label(id) == "ENTRY"):
        taxonomy.add_node_to_end(taxonomy.get_label(id), id)
    else:
        taxonomy.add_node_to_beginning(taxonomy.get_label(id), id)

@app.post("/{taxonomy_name}/{branch}/entry/{entry}")
async def editEntry(request: Request, branch: str, taxonomy_name: str, entry: str):
    """
    Editing an entry in a taxonomy.
    New key-value pairs can be added, old key-value pairs can be updated.
    URL will be of format '/entry/<id>'
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    incomingData = await request.json()
    result = taxonomy.update_nodes("ENTRY", entry, incomingData)
    updatedEntry = list(result)
    return updatedEntry

@app.post("/{taxonomy_name}/{branch}/entry/{entry}/children")
async def editEntryChildren(request: Request, branch: str, taxonomy_name: str, entry: str):
    """
    Editing an entry's children in a taxonomy.
    New children can be added, old children can be removed.
    URL will be of format '/entry/<id>/children'
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    incomingData = await request.json()
    result = taxonomy.update_node_children(entry, incomingData)
    updatedChildren = list(result)
    return updatedChildren

@app.post("/{taxonomy_name}/{branch}/synonym/{synonym}")
async def editSynonyms(request: Request, branch: str, taxonomy_name: str, synonym: str):
    """
    Editing a synonym in a taxonomy.
    New key-value pairs can be added, old key-value pairs can be updated.
    URL will be of format '/synonym/<id>'
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    incomingData = await request.json()
    result = taxonomy.update_nodes("SYNONYMS", synonym, incomingData)
    updatedSynonym = list(result)
    return updatedSynonym

@app.post("/{taxonomy_name}/{branch}/stopword/{stopword}")
async def editStopwords(request: Request, branch: str, taxonomy_name: str, stopword: str):
    """
    Editing a stopword in a taxonomy.
    New key-value pairs can be added, old key-value pairs can be updated.
    URL will be of format '/stopword/<id>'
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    incomingData = await request.json()
    result = taxonomy.update_nodes("STOPWORDS", stopword, incomingData)
    updatedStopword = list(result)
    return updatedStopword

@app.post("/{taxonomy_name}/{branch}/header")
async def editHeader(incomingData: Header, branch: str, taxonomy_name: str):
    """
    Editing the __header__ in a taxonomy.
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    convertedData = incomingData.dict()
    result = taxonomy.update_nodes("TEXT", "__header__", convertedData)
    updatedHeader = list(result)
    return updatedHeader

@app.post("/{taxonomy_name}/{branch}/footer")
async def editFooter(incomingData: Footer, branch: str, taxonomy_name: str):
    """
    Editing the __footer__ in a taxonomy.
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    convertedData = incomingData.dict()
    result = taxonomy.update_nodes("TEXT", "__footer__", convertedData)
    updatedFooter = list(result)
    return updatedFooter

# Delete methods

@app.delete("/{taxonomy_name}/{branch}/nodes")
async def deleteNode(request: Request, branch: str, taxonomy_name: str):
    """
    Deleting given node from a taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    incomingData = await request.json()
    id = incomingData["id"]
    taxonomy.delete_node(taxonomy.get_label(id), id)