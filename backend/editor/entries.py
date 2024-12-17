"""
Database helper functions for API
"""

import asyncio
import datetime
import logging
import shutil
import tempfile
import urllib.request  # Sending requests
from typing import Optional

from fastapi import BackgroundTasks, HTTPException, UploadFile

# For synchronous I/O-bound functions in async path operations/background tasks
from fastapi.concurrency import run_in_threadpool
from openfoodfacts_taxonomy_parser import parser  # Parser for taxonomies
from openfoodfacts_taxonomy_parser import unparser  # Unparser for taxonomies
from openfoodfacts_taxonomy_parser import patcher
from openfoodfacts_taxonomy_parser import utils as parser_utils

from . import settings, utils
from .controllers.node_controller import create_entry_node, get_error_node
from .controllers.project_controller import (
    create_project,
    edit_project,
    get_project,
    get_project_id,
)
from .exceptions import GithubBranchExistsError  # Custom exceptions
from .exceptions import (
    GithubUploadError,
    TaxonomyImportError,
    TaxonomyParsingError,
    TaxonomyUnparsingError,
)
from .github_functions import GithubOperations  # Github functions
from .graph_db import (  # Neo4J transactions context managers
    SyncTransactionCtx,
    TransactionCtx,
    get_current_transaction,
)
from .models.node_models import EntryNode, EntryNodeCreate, NodeType
from .models.project_models import ProjectCreate, ProjectEdit, ProjectStatus
from .settings import EXTERNAL_TAXONOMIES

log = logging.getLogger(__name__)


async def async_list(async_iterable):
    return [i async for i in async_iterable]


class TaxonomyGraph:
    """Class for database operations"""

    def __init__(self, branch_name, taxonomy_name):
        self.taxonomy_name = taxonomy_name
        self.branch_name = branch_name
        self.project_name = get_project_id(branch_name, taxonomy_name)

    def taxonomy_path_in_repository(self, taxonomy_name):
        return utils.taxonomy_path_in_repository(taxonomy_name)

    def get_label(self, id) -> NodeType:
        """
        Helper function for getting the label for a given id
        """
        if id.startswith("stopword"):
            return NodeType.STOPWORDS
        elif id.startswith("synonym"):
            return NodeType.SYNONYMS
        elif id.startswith("__header__") or id.startswith("__footer__"):
            return NodeType.TEXT
        else:
            return NodeType.ENTRY

    async def create_entry_node(self, name, main_language_code) -> str:
        """
        Helper function used to create an entry node with given name and main language
        """
        stopwords = await self.get_stopwords_dict()

        return await create_entry_node(
            self.project_name,
            EntryNodeCreate(name=name, main_language_code=main_language_code),
            stopwords,
        )

    async def get_local_taxonomy_file(self, tmpdir: str, uploadfile: UploadFile):
        filename = uploadfile.filename
        filepath = f"{tmpdir}/{filename}"
        with open(filepath, "wb") as f:
            await run_in_threadpool(shutil.copyfileobj, uploadfile.file, f)
        return filepath

    async def get_github_taxonomy_file(self, tmpdir: str, taxonomy_name: str):
        async with TransactionCtx():
            filepath = f"{tmpdir}/{taxonomy_name}.txt"
            path_in_repository = self.taxonomy_path_in_repository(taxonomy_name)
            target_url = (
                f"https://raw.githubusercontent.com/{settings.repo_uri}"
                f"/main/{path_in_repository}"
            )
            try:
                # get taxonomy file
                await run_in_threadpool(urllib.request.urlretrieve, target_url, filepath)
                if taxonomy_name == self.taxonomy_name:
                    # this is the taxonomy we want to edit
                    # track the current commit to know where to start the PR from
                    github_object = GithubOperations(self.taxonomy_name, self.branch_name)
                    commit_sha = (await github_object.get_branch("main")).commit.sha
                    file_sha = await github_object.get_file_sha()
                    await edit_project(
                        self.project_name,
                        ProjectEdit(
                            github_checkout_commit_sha=commit_sha, github_file_latest_sha=file_sha
                        ),
                    )
                return filepath
            except Exception as e:
                raise TaxonomyImportError() from e

    def parse_taxonomy(self, main_filepath: str, other_filepaths: list[str] | None = None):
        """
        Helper function to call the Open Food Facts Python Taxonomy Parser
        """
        with SyncTransactionCtx() as session:
            # Create parser object and pass current session to it
            parser_object = parser.Parser(session)
            try:
                # Parse taxonomy with given file name and branch name
                parser_object(main_filepath, other_filepaths, self.branch_name, self.taxonomy_name)
            except Exception as e:
                # outer exception handler will put project status to FAILED
                raise TaxonomyParsingError() from e

    async def get_and_parse_taxonomy(self, uploadfile: UploadFile | None = None):
        try:
            with tempfile.TemporaryDirectory(prefix="taxonomy-") as tmpdir:
                filepath = await (
                    self.get_github_taxonomy_file(tmpdir, self.taxonomy_name)
                    if uploadfile is None
                    else self.get_local_taxonomy_file(tmpdir, uploadfile)
                )
                other_filepaths = None
                if self.taxonomy_name in EXTERNAL_TAXONOMIES:
                    other_filepaths = await self.fetch_external_taxonomy_files(tmpdir)
                await run_in_threadpool(self.parse_taxonomy, filepath, other_filepaths)
                async with TransactionCtx():
                    error_node = await get_error_node(self.project_name)
                    errors_count = len(error_node.errors) if error_node else 0
                    await edit_project(
                        self.project_name,
                        ProjectEdit(status=ProjectStatus.OPEN, errors_count=errors_count),
                    )
        except Exception as e:
            async with TransactionCtx():
                error_node = await get_error_node(self.project_name)
                errors_count = len(error_node.errors) if error_node else 0
                await edit_project(
                    self.project_name,
                    ProjectEdit(status=ProjectStatus.FAILED, errors_count=errors_count),
                )
            log.exception(e)
            raise e

    async def fetch_external_taxonomy_files(self, tmpdir: str) -> list[str]:
        """
        Helper function to fetch external taxonomies concurrently from Github
        """
        external_taxonomy_filepaths = []
        tasks = []

        # Create tasks for each external taxonomy and store them in a list
        for external_taxonomy in EXTERNAL_TAXONOMIES[self.taxonomy_name]:
            task = asyncio.create_task(self.get_github_taxonomy_file(tmpdir, external_taxonomy))
            tasks.append(task)

        # Wait for all tasks to complete concurrently
        for task in tasks:
            external_filepath = await task
            external_taxonomy_filepaths.append(external_filepath)

        return external_taxonomy_filepaths

    async def import_taxonomy(
        self,
        description: str,
        owner_name: str,
        background_tasks: BackgroundTasks,
        uploadfile: UploadFile | None = None,
    ):
        """
        Helper function to import a taxonomy
        """
        await create_project(
            ProjectCreate(
                id=self.project_name,
                taxonomy_name=self.taxonomy_name,
                branch_name=self.branch_name,
                description=description,
                owner_name=owner_name,
                is_from_github=uploadfile is None,
            )
        )
        background_tasks.add_task(self.get_and_parse_taxonomy, uploadfile)
        return True

    def dump_taxonomy(
        self,
        background_tasks: BackgroundTasks,
        dump_cls: unparser.WriteTaxonomy = patcher.PatchTaxonomy,
    ):
        """
        Helper function to create the txt file of a taxonomy
        """
        # Create unparser object and pass a sync session to it
        with SyncTransactionCtx() as session:
            dumper = dump_cls(session)
            # Creates a unique file for dumping the taxonomy
            filename = self.project_name + ".txt"
            try:
                # Dump taxonomy with given file name and branch name
                dumper(filename, self.branch_name, self.taxonomy_name)
                # Program file removal in the background
                background_tasks.add_task(utils.file_cleanup, filename)
                return filename
            except Exception as e:
                log.exception(e)
                raise TaxonomyUnparsingError() from e

    async def file_export(self, background_tasks: BackgroundTasks):
        """Export a taxonomy for download"""
        filepath = await run_in_threadpool(self.dump_taxonomy, background_tasks)
        return filepath

    async def github_export(self, background_tasks: BackgroundTasks):
        """Export a taxonomy to Github"""
        filepath = await run_in_threadpool(self.dump_taxonomy, background_tasks)
        pr_url = await self.export_to_github(filepath)
        return pr_url

    async def export_to_github(self, filename):
        """
        Helper function to export a taxonomy to GitHub
        """
        project = await get_project(self.project_name)
        is_from_github, owner_name, status, description, commit_sha, file_sha, pr_url = (
            project.is_from_github,
            project.owner_name,
            project.status,
            project.description,
            project.github_checkout_commit_sha,
            project.github_file_latest_sha,
            project.github_pr_url,
        )

        if not is_from_github:
            raise HTTPException(
                status_code=422,
                detail=(
                    "This taxonomy was not imported from GitHub. It cannot be exported to GitHub"
                ),
            )

        github_object = GithubOperations(self.taxonomy_name, self.branch_name)

        if status != ProjectStatus.EXPORTED:
            try:
                await github_object.checkout_branch(commit_sha)
            except Exception as e:
                raise GithubBranchExistsError() from e

        try:
            new_file = await github_object.update_file(filename, file_sha, owner_name)

            if status != ProjectStatus.EXPORTED:
                pull_request = await github_object.create_pr(description)
                pr_url = pull_request.html_url

            await edit_project(
                self.project_name,
                ProjectEdit(
                    status=ProjectStatus.EXPORTED,
                    github_file_latest_sha=new_file.content.sha,
                    github_pr_url=pr_url,
                ),
            )
            return pr_url

        except Exception as e:
            raise GithubUploadError() from e

    async def does_project_exist(self):
        """
        Helper function to check the existence of a project
        """
        query = """MATCH (n:PROJECT) WHERE n.id = $project_name RETURN n"""
        result = await get_current_transaction().run(query, {"project_name": self.project_name})
        if (await result.value()) == []:
            return False
        else:
            return True

    async def is_branch_unique(self, from_github: bool):
        """
        Helper function to check uniqueness of branch
        """
        query = """MATCH (n:PROJECT) WHERE n.branch_name = $branch_name RETURN n"""
        result = await get_current_transaction().run(query, {"branch_name": self.branch_name})

        if not from_github:
            return (await result.value()) == []

        github_object = GithubOperations(self.taxonomy_name, self.branch_name)
        github_branch = await github_object.get_branch(self.branch_name)

        return (await result.value() == []) and (github_branch is None)

    def is_valid_branch_name(self):
        """
        Helper function to check if a branch name is valid
        """
        return parser_utils.normalize_text(self.branch_name, char="_") == self.branch_name

    async def list_projects(self, status=None):
        """
        Helper function for listing all existing projects created in Taxonomy Editor
        includes number of nodes with label ERROR for each project
        """
        query = [
            "MATCH (n:PROJECT)",
            "OPTIONAL MATCH (error_node:ERRORS {branch_name: n.branch_name, id: n.id})",
        ]

        params = {}
        if status is not None:
            # List only projects matching status
            query.append("WHERE n.status = $status")
            params["status"] = status

        query.extend(
            [
                "WITH n, size(error_node.errors) AS errors_count",
                "RETURN n{.*, errors_count: errors_count}",
                "ORDER BY n.created_at",
            ]
        )

        query_result = await get_current_transaction().run("\n".join(query), params)

        return [item async for result_list in query_result for item in result_list]

    async def add_node_to_end(self, label: NodeType, entry):
        """
        Helper function which adds an a newly created node to end of taxonomy
        """
        # Delete relationship between current last node and __footer__
        query = f"""
        MATCH (last_node)-[r:is_before]->(footer:{self.project_name}:TEXT)
            WHERE footer.id = "__footer__" DELETE r
        RETURN last_node
        """
        result = await get_current_transaction().run(query)
        end_node = (await result.data())[0]["last_node"]
        end_node_label = self.get_label(end_node["id"])  # Get current last node ID

        # Rebuild relationships by inserting incoming node at the end
        query = []
        query = f"""
            MATCH (new_node:{self.project_name}:{label.value}) WHERE new_node.id = $id
            MATCH (last_node:{self.project_name}:{end_node_label.value}) WHERE last_node.id = $endnodeid
            MATCH (footer:{self.project_name}:TEXT) WHERE footer.id = "__footer__"
            CREATE (last_node)-[:is_before]->(new_node)
            CREATE (new_node)-[:is_before]->(footer)
        """
        await get_current_transaction().run(query, {"id": entry, "endnodeid": end_node["id"]})

    # UNUSED FOR NOW
    async def add_node_to_beginning(self, label: NodeType, entry):
        """
        Helper function which adds an existing node to beginning of taxonomy
        """
        # Delete relationship between current first node and __header__
        query = f"""
            MATCH (header:{self.project_name}:TEXT)-[r:is_before]->(first_node)
                WHERE header.id = "__header__" DELETE r
            RETURN first_node
        """
        result = await get_current_transaction().run(query)
        start_node = await result.data()[0]["first_node"]
        start_node_label = self.get_label(start_node["id"])  # Get current first node ID

        # Rebuild relationships by inserting incoming node at the beginning
        query = f"""
            MATCH (new_node:{self.project_name}:{label.value}) WHERE new_node.id = $id
            MATCH (first_node:{self.project_name}:{start_node_label.value})
                WHERE first_node.id = $startnodeid
            MATCH (header:{self.project_name}:TEXT) WHERE header.id = "__header__"
            CREATE (new_node)-[:is_before]->(first_node)
            CREATE (header)-[:is_before]->(new_node)
        """
        await get_current_transaction().run(query, {"id": entry, "startnodeid": start_node["id"]})

    async def delete_node(self, label: NodeType, entry):
        """
        Helper function used for deleting a node with given id and label

        We don't really delete it because we have to keep track of modified nodes.
        We set the entry type label to REMOVED_<label>
        """
        modified = datetime.datetime.now().timestamp()
        # Remove node from is_before relation and attach node previous node to next node
        query = f"""
            // Find node to be deleted using node ID
            MATCH (deleted_node:{self.project_name}:{label.value})-[:is_before]->(next_node)
                WHERE deleted_node.id = $id
            MATCH (previous_node)-[:is_before]->(deleted_node)
            // Remove node
            DETACH (deleted_node)
            // Rebuild relationships after deletion
            CREATE (previous_node)-[:is_before]->(next_node)
        """
        await get_current_transaction().run(query, {"id": entry})
        # transfert child parent relations, and mark child nodes as modified
        query = f"""
            // Find relations to be removed using node ID
            MATCH (child_node)-[:is_child_of]->(deleted_node:{self.project_name}:{label.value})
                WHERE deleted_node.id = $id
            MATCH (deleted_node)-[:is_child_of]->(parent_node)
            DETACH (deleted_node)
            // transfer child
            CREATE (child_node) -[:is_child_of]->(parent_node)
            // mark modified
            SET child_node.modified = $modified
        """
        await get_current_transaction().run(query, {"id": entry, "modified": modified})
        # change label of node to be deleted
        query = f"""
            MATCH (deleted_node:{self.project_name}:{label.value})
            WHERE deleted_node.id = $id
            REMOVE deleted_node:{label.value}
            SET deleted_node:REMOVED_{label.value}
            // and mark modification date also
            SET deleted_node.modified = $modified
        """
        result = await get_current_transaction().run(query, {"id": entry})
        return await async_list(result)

    async def get_all_nodes(self, label: Optional[NodeType] = None, removed: bool = False):
        """
        Helper function used for getting all nodes with/without given label
        """
        labels = [label.value] if label else [label.value for label in NodeType]
        if removed:
            labels = [f"REMOVED_{label}" for label in labels]
        query = f"""
            MATCH (n:{self.project_name}:{"|".join(labels)}) RETURN n
        """
        result = await get_current_transaction().run(query)
        return await async_list(result)

    async def get_all_root_nodes(self):
        """
        Helper function used for getting all root nodes in a taxonomy
        """
        query = f"""
            MATCH (n:{self.project_name}:ENTRY)
            WHERE NOT (n)-[:is_child_of]->()
            RETURN n
        """
        result = await get_current_transaction().run(query)
        return await async_list(result)

    async def get_parsing_errors(self):
        """
        Helper function used for getting parsing errors in the current project
        """
        # During parsing of a taxonomy, all the parsing errors
        # are stored in a separate node with the label "ERRORS"
        # This function returns all the parsing errors
        query = f"""
            MATCH (
                error_node:ERRORS
                {{branch_name: "{self.branch_name}", id: "{self.project_name}"}}
            )
            RETURN error_node
        """
        result = await get_current_transaction().run(query)
        error_node = (await result.data())[0]["error_node"]
        return error_node

    async def get_nodes(self, label: NodeType, entry):
        """
        Helper function used for getting the node with given id and label
        """
        query = f"""
            MATCH (n:{self.project_name}:{label.value}) WHERE n.id = $id
            RETURN n
        """
        result = await get_current_transaction().run(query, {"id": entry})
        return await async_list(result)

    async def get_parents(self, entry):
        """
        Helper function used for getting node parents with given id
        """
        query = f"""
            MATCH (child_node:{self.project_name}:ENTRY)-[r:is_child_of]->(parent)
                WHERE child_node.id = $id
            RETURN parent.id
            ORDER BY r.position
        """
        query_result = await get_current_transaction().run(query, {"id": entry})
        return [item async for result_list in query_result for item in result_list]

    async def get_children(self, entry):
        """
        Helper function used for getting node children with given id
        """
        query = f"""
            MATCH (child)-[r:is_child_of]->(parent_node:{self.project_name}:ENTRY)
                WHERE parent_node.id = $id
            RETURN child.id
        """
        result = await get_current_transaction().run(query, {"id": entry})
        return await async_list(result)

    async def get_stopwords_dict(self) -> dict[str, list[str]]:
        """
        Helper function used for getting all stopwords in a taxonomy, in the form of a dictionary
        where the keys are the language codes, and the values are the stopwords in the
        corresponding language
        """
        query = f"""
            MATCH (s:{self.project_name}:STOPWORDS)
            WITH keys(s) AS properties, s
            UNWIND properties AS property
            WITH s, property
            WHERE property STARTS WITH 'tags_ids'
            RETURN property AS tags_ids_lc, s[property] AS stopwords
        """
        result = await get_current_transaction().run(query)
        records = await async_list(result)
        stopwords_dict = {
            record["tags_ids_lc"].split("_")[-1]: record["stopwords"] for record in records
        }
        return stopwords_dict

    async def update_node(self, label: NodeType, new_node: EntryNode):
        """
        Helper function used for updation of node with given id and label
        """
        # Get current node information and deleted keys
        result = await self.get_nodes(label, new_node.id)
        curr_node = EntryNode(**result[0]["n"])

        # Recompute normalized tags ids corresponding to entry tags
        stopwords = await self.get_stopwords_dict()
        new_node.recompute_tags_ids(stopwords)

        # Build query
        query = [f"""MATCH (n:{self.project_name}:{label.value}) WHERE n.id = $id """]

        modified = datetime.datetime.now().timestamp()
        query.append(f"""\nSET n.modified = {modified}""")

        # Delete keys removed by user
        deleted_keys = (
            (set(curr_node.tags.keys()) - set(new_node.tags.keys()))
            | (set(curr_node.tags_ids.keys()) - set(new_node.tags_ids.keys()))
            | (set(curr_node.properties.keys()) - set(new_node.properties.keys()))
            | (set(curr_node.comments.keys()) - set(new_node.comments.keys()))
        )
        for key in deleted_keys:
            query.append(f"""\nREMOVE n.{key}\n""")

        # Update keys
        data = new_node.flat_dict()
        for key in data.keys():
            query.append(f"""\nSET n.{key} = ${key}\n""")

        # Update id if first translation of the main language has changed
        new_node.recompute_id()
        id_changed = new_node.id != curr_node.id
        if id_changed:
            # check it does not already exists
            if len(await self.get_nodes(label, new_node.id)) != 0:
                raise HTTPException(
                    status_code=400,
                    detail=(f"Can't change node id, entry {new_node.id} already exists"),
                )
            query.append("""\nSET n.id = $id\n""")

        query.append("""RETURN n""")
        params = dict(data)
        log.debug("update_node query: %s \nParam:%s", " ".join(query), params)
        result = await get_current_transaction().run(" ".join(query), params)
        updated_node = (await async_list(result))[0]["n"]
        if id_changed:
            # mark children as modified because the parent id has changed
            query = f"""
            MATCH (child:{self.project_name}:ENTRY) - [:is_child_of] -> (parent:{self.project_name}:ENTRY)
            WHERE parent.id = $id
            SET child.modified = $modified
            """
            await get_current_transaction().run(query, {"id": updated_node["id"], "modified": modified})
        return updated_node

    async def update_node_children(self, entry, new_children_ids):
        """
        Helper function used for updation of node children with given id
        """
        modified = datetime.datetime.now().timestamp()
        # Parse node ids from Neo4j Record object
        current_children = [record["child.id"] for record in list(await self.get_children(entry))]
        deleted_children = list(set(current_children) - set(new_children_ids))
        added_children = set(new_children_ids) - set(current_children)

        # Delete relationships
        query = f"""
            MATCH
                (deleted_child:{self.project_name}:ENTRY)
                -[rel:is_child_of]->
                (parent:{self.project_name}:ENTRY)
            WHERE parent.id = $id AND deleted_child.id IN $children
            DELETE rel
        """
        await get_current_transaction().run(query, {"id": entry, "children": deleted_children})
        # update children modified property
        query = f"""
            MATCH (child:{self.project_name}:ENTRY)
            WHERE child.id in $children
            SET child.modified = $modified
        """
        await get_current_transaction().run(
            query, {"children": deleted_children, "modified": modified}
        )

        # get non-existing nodes
        query = f"""
            MATCH (child:{self.project_name}:ENTRY)
                WHERE child.id in $ids RETURN child.id
        """
        _result = await get_current_transaction().run(query, ids=list(added_children))
        existing_ids = [record["child.id"] for record in (await _result.data())]
        to_create = added_children - set(existing_ids)

        # Normalising new children node ID
        created_child_ids = []
        # create new nodes
        for child in to_create:
            main_language_code, child_name = child.split(":", 1)
            created_node_id = await self.create_entry_node(child_name, main_language_code)
            created_child_ids.append(created_node_id)

            # TODO: We would prefer to add the node just after its parent entry
            await self.add_node_to_end(NodeType.ENTRY, created_node_id)

        # Stores result of last query executed
        result = []
        children_ids = created_child_ids + existing_ids
        for child_id in children_ids:
            # Create new relationships if it doesn't exist
            query = f"""
                MATCH (parent:{self.project_name}:ENTRY), (new_child:{self.project_name}:ENTRY)
                WHERE parent.id = $id AND new_child.id = $child_id
                OPTIONAL MATCH ()-[r:is_child_of]->(parent)
                WITH parent, new_child, COUNT(r) AS rel_count
                MERGE (new_child)-[r:is_child_of]->(parent)
                ON CREATE SET r.position = CASE WHEN rel_count IS NULL THEN 1 ELSE rel_count + 1 END
            """
            _result = await get_current_transaction().run(
                query, {"id": entry, "child_id": child_id}
            )
            result = list(await _result.value())
        # update modified of existing but added children entries
        # update children modified property
        query = f"""
            MATCH (child:{self.project_name}:ENTRY)
            WHERE child.id in $children
            SET child.modified = $modified
        """
        await get_current_transaction().run(query, {"children": existing_ids, "modified": modified})

        return result
