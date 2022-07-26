from dependencies import *
from entries import *

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
    initialize_db()

@app.on_event("shutdown")
async def shutdown():
    """
    Close session and driver of Neo4J database
    """
    shutdown_db()

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

    if len(oneEntry) == 0:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    return oneEntry

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

    if len(oneSynonym) == 0:
        raise HTTPException(status_code=404, detail="Entry not found")

    return oneSynonym

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
    
    if len(oneStopword) == 0:
        raise HTTPException(status_code=404, detail="Entry not found")

    return oneStopword

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
    result = get_marginals("__header__")
    header = list(result)
    return header

@app.get("/footer")
async def findFooter(response: Response):
    """
    Get __footer__ within taxonomy
    """
    result = get_marginals("__footer__")
    footer = list(result)
    return footer

# Put methods 

@app.put("/edit/entry/{entry}")
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

@app.put("/edit/synonym/{synonym}")
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

@app.put("/edit/stopword/{stopword}")
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

@app.put("/edit/header")
async def editHeader(incomingData: Header):
    """
    Editing the __header__ in a taxonomy.
    """
    result = update_marginals("__header__", incomingData)
    updatedHeader = list(result)
    return updatedHeader

@app.put("/edit/footer")
async def editFooter(incomingData: Footer):
    """
    Editing the __footer__ in a taxonomy.
    """
    result = update_marginals("__footer__", incomingData)
    updatedFooter = list(result)
    return updatedFooter