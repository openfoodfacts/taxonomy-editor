"""
Taxonomy Editor Backend API
"""

import contextlib
import logging

# Required imports
# ------------------------------------------------------------------------------------#
from datetime import datetime
from typing import Annotated, Optional

# FastAPI
from fastapi import (
    BackgroundTasks,
    FastAPI,
    Form,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

# DB helper imports
from . import graph_db

# Controller imports
from .controllers import node_controller, project_controller, search_controller
from .entries import TaxonomyGraph

# Custom exceptions
from .exceptions import GithubBranchExistsError, GithubUploadError

# Data model imports
from .models.node_models import EntryNode, EntryNodeCreate, ErrorNode, NodeType
from .models.project_models import Project, ProjectEdit, ProjectStatus
from .models.search_models import EntryNodeSearchResult
from .scheduler import scheduler_lifespan

# -----------------------------------------------------------------------------------#

# Setup logs
logging.basicConfig(
    handlers=[logging.StreamHandler()],
    level=logging.INFO,
)

log = logging.getLogger(__name__)


# Setup FastAPI app lifespan
@contextlib.asynccontextmanager
async def app_lifespan(app: FastAPI):
    async with graph_db.database_lifespan():
        with scheduler_lifespan():
            yield


app = FastAPI(title="Open Food Facts Taxonomy Editor API", lifespan=app_lifespan)

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


@app.middleware("http")
async def initialize_neo4j_transactions(request: Request, call_next):
    async with graph_db.TransactionCtx():
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    reformatted_errors = []
    for pydantic_error in exc.errors():
        # Add custom message for status filter
        if pydantic_error["loc"] == ("query", "status"):
            pydantic_error["msg"] = (
                "Status filter must be one of: OPEN, CLOSED or should be omitted"
            )
        reformatted_errors.append(pydantic_error)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"detail": "Invalid request", "errors": reformatted_errors}),
    )


@app.exception_handler(HTTPException)
async def log_http_exception(request: Request, exc: HTTPException):
    """
    Custom exception handler to log FastAPI exceptions.
    """
    # Log the detail message
    log.info(f" ERROR: {exc.detail}")
    return await http_exception_handler(request, exc)


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
async def get_all_projects() -> list[Project]:
    """
    List projects created in the Taxonomy Editor
    """
    return await project_controller.get_all_projects()


@app.get("/{taxonomy_name}/{branch}/project")
async def get_project_info(branch: str, taxonomy_name: str) -> Project:
    """
    Get information about a Taxonomy Editor project
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = await project_controller.get_project(taxonomy.project_name)
    return result


@app.get("/{taxonomy_name}/{branch}/set-project-status")
async def set_project_status(
    response: Response, branch: str, taxonomy_name: str, status: Optional[ProjectStatus] = None
):
    """
    Set the status of a Taxonomy Editor project
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = await project_controller.edit_project(
        taxonomy.project_name, ProjectEdit(status=status)
    )
    return result


@app.get("/{taxonomy_name}/{branch}/nodes")
async def find_all_nodes(response: Response, branch: str, taxonomy_name: str):
    """
    Get all nodes within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    all_nodes = await taxonomy.get_all_nodes()
    return all_nodes


@app.get("/{taxonomy_name}/{branch}/rootentries")
async def find_all_root_nodes(response: Response, branch: str, taxonomy_name: str):
    """
    Get all root nodes within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    all_root_nodes = await taxonomy.get_all_root_nodes()
    return all_root_nodes


@app.get("/{taxonomy_name}/{branch}/entry/{entry}")
async def find_one_entry(branch: str, taxonomy_name: str, entry: str) -> EntryNode:
    """
    Get entry corresponding to id within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    return await node_controller.get_entry_node(taxonomy.project_name, entry)


@app.get("/{taxonomy_name}/{branch}/entry/{entry}/parents")
async def find_one_entry_parents(response: Response, branch: str, taxonomy_name: str, entry: str):
    """
    Get parents for a entry corresponding to id within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    one_entry_parents = await taxonomy.get_parents(entry)

    return one_entry_parents


@app.get("/{taxonomy_name}/{branch}/entry/{entry}/children")
async def find_one_entry_children(response: Response, branch: str, taxonomy_name: str, entry: str):
    """
    Get children for a entry corresponding to id within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    one_entry_children = await taxonomy.get_children(entry)

    return one_entry_children


@app.get("/{taxonomy_name}/{branch}/synonym/{synonym}")
async def find_one_synonym(response: Response, branch: str, taxonomy_name: str, synonym: str):
    """
    Get synonym corresponding to id within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    one_synonym = await taxonomy.get_nodes(NodeType.SYNONYMS, synonym)

    check_single(one_synonym)

    return one_synonym[0]


@app.get("/{taxonomy_name}/{branch}/synonym")
async def find_all_synonyms(response: Response, branch: str, taxonomy_name: str):
    """
    Get all synonyms within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    all_synonyms = await taxonomy.get_all_nodes(NodeType.SYNONYMS)
    return all_synonyms


@app.get("/{taxonomy_name}/{branch}/stopword/{stopword}")
async def find_one_stopword(response: Response, branch: str, taxonomy_name: str, stopword: str):
    """
    Get stopword corresponding to id within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    one_stopword = await taxonomy.get_nodes(NodeType.STOPWORDS, stopword)

    check_single(one_stopword)

    return one_stopword[0]


@app.get("/{taxonomy_name}/{branch}/stopword")
async def find_all_stopwords(response: Response, branch: str, taxonomy_name: str):
    """
    Get all stopwords within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    all_stopwords = await taxonomy.get_all_nodes(NodeType.STOPWORDS)
    return all_stopwords


@app.get("/{taxonomy_name}/{branch}/header")
async def find_header(response: Response, branch: str, taxonomy_name: str):
    """
    Get __header__ within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    header = await taxonomy.get_nodes(NodeType.TEXT, "__header__")
    return header[0]


@app.get("/{taxonomy_name}/{branch}/footer")
async def find_footer(response: Response, branch: str, taxonomy_name: str):
    """
    Get __footer__ within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    footer = await taxonomy.get_nodes(NodeType.TEXT, "__footer__")
    return footer[0]


@app.get("/{taxonomy_name}/{branch}/parsing_errors")
async def find_all_errors(branch: str, taxonomy_name: str) -> ErrorNode:
    """
    Get all errors within taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = await taxonomy.get_parsing_errors()
    return result


@app.get("/{taxonomy_name}/{branch}/nodes/entry")
async def search_entry_nodes(
    branch: str,
    taxonomy_name: str,
    q: Annotated[
        str,
        Query(
            description="The search query string to filter down the returned entry nodes.\
            Example: is:root language:en not(language):fr"
        ),
    ] = "",
    page: int = 1,
) -> EntryNodeSearchResult:
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    result = await search_controller.search_entry_nodes(taxonomy.project_name, q, page)
    return result


@app.get("/{taxonomy_name}/{branch}/downloadexport")
async def export_to_text_file(
    response: Response, branch: str, taxonomy_name: str, background_tasks: BackgroundTasks
):
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    file = await taxonomy.file_export(background_tasks)

    return FileResponse(file)


@app.get("/{taxonomy_name}/{branch}/githubexport")
async def export_to_github(
    response: Response, branch: str, taxonomy_name: str, background_tasks: BackgroundTasks
):
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    try:
        url = await taxonomy.github_export(background_tasks)
        return url

    except GithubBranchExistsError:
        raise HTTPException(status_code=409, detail="The Github branch already exists!")

    except GithubUploadError:
        raise HTTPException(status_code=400, detail="Github upload error!")


# Post methods


@app.post("/{taxonomy_name}/{branch}/import")
async def import_from_github(
    request: Request,
    response: Response,
    branch: str,
    taxonomy_name: str,
    background_tasks: BackgroundTasks,
):
    """
    Get taxonomy from Product Opener GitHub repository
    """
    incoming_data = await request.json()
    description = incoming_data["description"]
    ownerName = incoming_data["ownerName"]

    taxonomy = TaxonomyGraph(branch, taxonomy_name)

    if not taxonomy.is_valid_branch_name():
        raise HTTPException(status_code=422, detail="branch_name: Enter a valid branch name!")
    if await taxonomy.does_project_exist():
        raise HTTPException(status_code=409, detail="Project already exists!")
    if not await taxonomy.is_branch_unique(from_github=True):
        raise HTTPException(status_code=409, detail="branch_name: Branch name should be unique!")

    status = await taxonomy.import_taxonomy(description, ownerName, background_tasks)
    # TODO: temporary fix - https://github.com/openfoodfacts/taxonomy-editor/issues/401
    response.headers["Connection"] = "close"
    return status


@app.post("/{taxonomy_name}/{branch}/upload")
async def upload_taxonomy(
    branch: str,
    taxonomy_name: str,
    file: UploadFile,
    background_tasks: BackgroundTasks,
    description: str = Form(...),
):
    """
    Upload taxonomy file to be parsed
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    if not taxonomy.is_valid_branch_name():
        raise HTTPException(status_code=422, detail="branch_name: Enter a valid branch name!")
    if await taxonomy.does_project_exist():
        raise HTTPException(status_code=409, detail="Project already exists!")
    if not await taxonomy.is_branch_unique(from_github=False):
        raise HTTPException(status_code=409, detail="branch_name: Branch name should be unique!")

    result = await taxonomy.import_taxonomy(description, "unknown", background_tasks, file)

    return result


@app.post("/{taxonomy_name}/{branch}/entry", status_code=status.HTTP_201_CREATED)
async def create_entry_node(
    branch: str, taxonomy_name: str, new_entry_node: EntryNodeCreate
) -> None:
    """
    Creating a new entry node in a taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    normalized_id = await taxonomy.create_entry_node(
        new_entry_node.name, new_entry_node.main_language_code
    )
    await taxonomy.add_node_to_end(NodeType.ENTRY, normalized_id)


@app.post("/{taxonomy_name}/{branch}/entry/{entry}")
async def edit_entry(request: Request, branch: str, taxonomy_name: str, entry: str):
    """
    Editing an entry in a taxonomy.
    New key-value pairs can be added, old key-value pairs can be updated.
    URL will be of format '/entry/<id>'
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    incoming_data = await request.json()
    incoming_data["id"] = entry
    new_entry = EntryNode(**incoming_data)
    updated_entry = await taxonomy.update_node(NodeType.ENTRY, new_entry)
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
    updated_children = await taxonomy.update_node_children(entry, incoming_data)
    return updated_children


# Delete methods


@app.delete("/{taxonomy_name}/{branch}/nodes")
async def delete_node(request: Request, branch: str, taxonomy_name: str):
    """
    Deleting given node from a taxonomy
    """
    taxonomy = TaxonomyGraph(branch, taxonomy_name)
    incoming_data = await request.json()
    id = incoming_data["id"]
    await taxonomy.delete_node(taxonomy.get_label(id), id)


@app.delete("/{taxonomy_name}/{branch}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(branch: str, taxonomy_name: str):
    """
    Delete a project
    """
    project_id = project_controller.get_project_id(branch, taxonomy_name)
    await project_controller.delete_project(project_id)
