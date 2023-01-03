"""
Taxonomy Editor Backend API
"""
import logging
import os

# Required imports
# ----------------------------------------------------------------------------#
from datetime import datetime

# FastAPI
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# DB helper imports
from . import graph_db
from .entries import TaxonomyGraph

# Custom exceptions
from .exceptions import GithubBranchExistsError, GithubUploadError

# Data model imports
from .models import Footer, Header

# ----------------------------------------------------------------------------#

# Setup logs
logging.basicConfig(
    handlers=[logging.StreamHandler()],
    level=logging.INFO,
)

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
    allow_origin_regex="https?://.*",
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


def file_cleanup(filepath):
    """
    Helper function to delete a taxonomy file from local storage
    """
    try:
        os.remove(filepath)
    except Exception:
        raise HTTPException(status_code=500, detail="Taxonomy file not found for deletion")


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


@app.get("/projects")
async def list_all_projects(response: Response):
    """
    List all open projects created in the Taxonomy Editor
    """
    # Listing all projects doesn't require a taoxnomy name or branch name
    taxonony = TaxonomyGraph("", "")
    result = list(taxonony.list_existing_projects())
    return result


@app.get("/{taxonomy_name}/{branch}/nodes")
async def find_all_nodes(response: Response, branch: str, taxonomy_name: str):
    """
    Get all nodes within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_all_nodes("")
    all_nodes = list(result)
    return all_nodes


@app.get("/{taxonomy_name}/{branch}/rootnodes")
async def find_all_root_nodes(response: Response, branch: str, taxonomy_name: str):
    """
    Get all root nodes within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_all_root_nodes()
    all_root_nodes = list(result)
    return all_root_nodes


@app.get("/{taxonomy_name}/{branch}/entry/{entry}")
async def find_one_entry(response: Response, branch: str, taxonomy_name: str, entry: str):
    """
    Get entry corresponding to id within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_nodes("ENTRY", entry)
    one_entry = list(result)

    check_single(one_entry)

    return one_entry[0]


@app.get("/{taxonomy_name}/{branch}/entry/{entry}/parents")
async def find_one_entry_parents(response: Response, branch: str, taxonomy_name: str, entry: str):
    """
    Get parents for a entry corresponding to id within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_parents(entry)
    one_entry_parents = list(result)

    return one_entry_parents


@app.get("/{taxonomy_name}/{branch}/entry/{entry}/children")
async def find_one_entry_children(response: Response, branch: str, taxonomy_name: str, entry: str):
    """
    Get children for a entry corresponding to id within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_children(entry)
    one_entry_children = list(result)

    return one_entry_children


@app.get("/{taxonomy_name}/{branch}/entry")
async def find_all_entries(response: Response, branch: str, taxonomy_name: str):
    """
    Get all entries within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_all_nodes("ENTRY")
    all_entries = list(result)
    return all_entries


@app.get("/{taxonomy_name}/{branch}/synonym/{synonym}")
async def find_one_synonym(response: Response, branch: str, taxonomy_name: str, synonym: str):
    """
    Get synonym corresponding to id within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_nodes("SYNONYMS", synonym)
    one_synonym = list(result)

    check_single(one_synonym)

    return one_synonym[0]


@app.get("/{taxonomy_name}/{branch}/synonym")
async def find_all_synonyms(response: Response, branch: str, taxonomy_name: str):
    """
    Get all synonyms within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_all_nodes("SYNONYMS")
    all_synonyms = list(result)
    return all_synonyms


@app.get("/{taxonomy_name}/{branch}/stopword/{stopword}")
async def find_one_stopword(response: Response, branch: str, taxonomy_name: str, stopword: str):
    """
    Get stopword corresponding to id within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_nodes("STOPWORDS", stopword)
    one_stopword = list(result)

    check_single(one_stopword)

    return one_stopword[0]


@app.get("/{taxonomy_name}/{branch}/stopword")
async def find_all_stopwords(response: Response, branch: str, taxonomy_name: str):
    """
    Get all stopwords within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_all_nodes("STOPWORDS")
    all_stopwords = list(result)
    return all_stopwords


@app.get("/{taxonomy_name}/{branch}/header")
async def find_header(response: Response, branch: str, taxonomy_name: str):
    """
    Get __header__ within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_nodes("TEXT", "__header__")
    header = list(result)
    return header[0]


@app.get("/{taxonomy_name}/{branch}/footer")
async def find_footer(response: Response, branch: str, taxonomy_name: str):
    """
    Get __footer__ within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_nodes("TEXT", "__footer__")
    footer = list(result)
    return footer[0]

@app.get("/{taxonomy_name}/{branch}/parsing_errors")
async def find_all_errors(request: Request, branch: str, taxonomy_name: str):
    """
    Get all errors within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.get_parsing_errors()
    return result

@app.get("/{taxonomy_name}/{branch}/search")
async def search_node(response: Response, branch: str, taxonomy_name: str, query: str):
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = taxonomy.full_text_search(query)
    return result


@app.get("/{taxonomy_name}/{branch}/downloadexport")
async def export_to_text_file(
    response: Response, branch: str, taxonomy_name: str, background_tasks: BackgroundTasks
):
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    file = taxonomy.file_export()

    # Add a background task for removing exported taxonomy file
    background_tasks.add_task(file_cleanup, file)
    return FileResponse(file)


@app.get("/{taxonomy_name}/{branch}/githubexport")
async def export_to_github(
    response: Response, branch: str, taxonomy_name: str, background_tasks: BackgroundTasks
):
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    try:
        url, file = taxonomy.github_export()
        # Add a background task for removing exported taxonomy file
        background_tasks.add_task(file_cleanup, file)
        return url

    except GithubBranchExistsError:
        raise HTTPException(status_code=500, detail="The Github branch already exists!")

    except GithubUploadError:
        raise HTTPException(status_code=500, detail="Github upload error!")


# Post methods


@app.post("/{taxonomy_name}/{branch}/import")
async def import_from_github(request: Request, branch: str, taxonomy_name: str):
    """
    Get taxonomy from Product Opener GitHub repository
    """
    incoming_data = await request.json()
    description = incoming_data["description"]

    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    if not taxonomy.is_valid_branch_name():
        raise HTTPException(status_code=500, detail="Enter a valid branch name!")
    if taxonomy.does_project_exist():
        raise HTTPException(status_code=500, detail="Project already exists!")
    if not taxonomy.is_branch_unique():
        raise HTTPException(status_code=500, detail="Branch name should be unique!")

    result = taxonomy.import_from_github(description)
    return result


@app.post("/{taxonomy_name}/{branch}/nodes")
async def create_node(request: Request, branch: str, taxonomy_name: str):
    """
    Creating a new node in a taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    incoming_data = await request.json()
    id = incoming_data["id"]
    main_language = incoming_data["main_language"]
    if id is None:
        raise HTTPException(status_code=400, detail="Invalid id")
    if main_language is None:
        raise HTTPException(status_code=400, detail="Invalid main language code")

    normalized_id = taxonomy.create_node(taxonomy.get_label(id), id, main_language)
    if taxonomy.get_label(id) == "ENTRY":
        taxonomy.add_node_to_end(taxonomy.get_label(normalized_id), normalized_id)
    else:
        taxonomy.add_node_to_beginning(taxonomy.get_label(normalized_id), normalized_id)


@app.post("/{taxonomy_name}/{branch}/entry/{entry}")
async def edit_entry(request: Request, branch: str, taxonomy_name: str, entry: str):
    """
    Editing an entry in a taxonomy.
    New key-value pairs can be added, old key-value pairs can be updated.
    URL will be of format '/entry/<id>'
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    incoming_data = await request.json()
    result = taxonomy.update_nodes("ENTRY", entry, incoming_data)
    updated_entry = list(result)
    return updated_entry


@app.post("/{taxonomy_name}/{branch}/entry/{entry}/children")
async def edit_entry_children(request: Request, branch: str, taxonomy_name: str, entry: str):
    """
    Editing an entry's children in a taxonomy.
    New children can be added, old children can be removed.
    URL will be of format '/entry/<id>/children'
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    incoming_data = await request.json()
    result = taxonomy.update_node_children(entry, incoming_data)
    updated_children = list(result)
    return updated_children


@app.post("/{taxonomy_name}/{branch}/synonym/{synonym}")
async def edit_synonyms(request: Request, branch: str, taxonomy_name: str, synonym: str):
    """
    Editing a synonym in a taxonomy.
    New key-value pairs can be added, old key-value pairs can be updated.
    URL will be of format '/synonym/<id>'
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    incoming_data = await request.json()
    result = taxonomy.update_nodes("SYNONYMS", synonym, incoming_data)
    updated_synonym = list(result)
    return updated_synonym


@app.post("/{taxonomy_name}/{branch}/stopword/{stopword}")
async def edit_stopwords(request: Request, branch: str, taxonomy_name: str, stopword: str):
    """
    Editing a stopword in a taxonomy.
    New key-value pairs can be added, old key-value pairs can be updated.
    URL will be of format '/stopword/<id>'
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    incoming_data = await request.json()
    result = taxonomy.update_nodes("STOPWORDS", stopword, incoming_data)
    updated_stopword = list(result)
    return updated_stopword


@app.post("/{taxonomy_name}/{branch}/header")
async def edit_header(incoming_data: Header, branch: str, taxonomy_name: str):
    """
    Editing the __header__ in a taxonomy.
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    convertedData = incoming_data.dict()
    result = taxonomy.update_nodes("TEXT", "__header__", convertedData)
    updated_header = list(result)
    return updated_header


@app.post("/{taxonomy_name}/{branch}/footer")
async def edit_footer(incoming_data: Footer, branch: str, taxonomy_name: str):
    """
    Editing the __footer__ in a taxonomy.
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    convertedData = incoming_data.dict()
    result = taxonomy.update_nodes("TEXT", "__footer__", convertedData)
    updated_footer = list(result)
    return updated_footer


# Delete methods


@app.delete("/{taxonomy_name}/{branch}/nodes")
async def delete_node(request: Request, branch: str, taxonomy_name: str):
    """
    Deleting given node from a taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    incoming_data = await request.json()
    id = incoming_data["id"]
    taxonomy.delete_node(taxonomy.get_label(id), id)
