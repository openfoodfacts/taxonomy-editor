"""
Database helper functions for API
"""
import re
import shutil
import tempfile
import urllib.request  # Sending requests

from fastapi import BackgroundTasks, HTTPException, UploadFile

# For synchronous I/O-bound functions in async path operations/background tasks
from fastapi.concurrency import run_in_threadpool
from openfoodfacts_taxonomy_parser import parser  # Parser for taxonomies
from openfoodfacts_taxonomy_parser import unparser  # Unparser for taxonomies
from openfoodfacts_taxonomy_parser import utils as parser_utils

from . import settings
from .controllers.project_controller import create_project, edit_project, get_project
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
from .models.project_models import ProjectCreate, ProjectEdit, ProjectStatus
from .utils import file_cleanup


async def async_list(async_iterable):
    return [i async for i in async_iterable]


class TaxonomyGraph:

    """Class for database operations"""

    def __init__(self, branch_name, taxonomy_name):
        self.taxonomy_name = taxonomy_name
        self.branch_name = branch_name
        self.project_name = "p_" + taxonomy_name + "_" + branch_name

    def get_label(self, id):
        """
        Helper function for getting the label for a given id
        """
        if id.startswith("stopword"):
            return "STOPWORDS"
        elif id.startswith("synonym"):
            return "SYNONYMS"
        elif id.startswith("__header__") or id.startswith("__footer__"):
            return "TEXT"
        else:
            return "ENTRY"

    async def create_node(self, label, entry, main_language_code):
        """
        Helper function used for creating a node with given id and label
        """
        params = {"id": entry}
        query = [f"""CREATE (n:{self.project_name}:{label})\n"""]
        stopwords = await self.get_stopwords_dict()

        # Build all basic keys of a node
        if label == "ENTRY":
            # Normalizing new canonical tag
            language_code, canonical_tag = entry.split(":", 1)
            normalised_canonical_tag = parser_utils.normalize_text(
                canonical_tag, main_language_code, stopwords=stopwords
            )

            # Reconstructing and updation of node ID
            params["id"] = language_code + ":" + normalised_canonical_tag
            params["main_language_code"] = main_language_code

            query.append(
                """ SET n.main_language = $main_language_code """
            )  # Required for only an entry
        else:
            canonical_tag = ""

        query.append(""" SET n.id = $id """)
        query.append(f""" SET n.tags_{main_language_code} = [$canonical_tag] """)
        query.append(""" SET n.preceding_lines = [] """)
        query.append(""" RETURN n.id """)

        params["canonical_tag"] = canonical_tag
        result = await get_current_transaction().run(" ".join(query), params)
        return (await result.data())[0]["n.id"]

    async def get_local_taxonomy_file(self, tmpdir: str, uploadfile: UploadFile):
        filename = uploadfile.filename
        filepath = f"{tmpdir}/{filename}"
        with open(filepath, "wb") as f:
            await run_in_threadpool(shutil.copyfileobj, uploadfile.file, f)
        return filepath

    async def get_github_taxonomy_file(self, tmpdir: str):
        async with TransactionCtx():
            filename = f"{self.taxonomy_name}.txt"
            filepath = f"{tmpdir}/{filename}"
            base_url = (
                "https://raw.githubusercontent.com/" + settings.repo_uri + "/main/taxonomies/"
            )
            try:
                await run_in_threadpool(urllib.request.urlretrieve, base_url + filename, filepath)
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

    def parse_taxonomy(self, filepath: str):
        """
        Helper function to call the Open Food Facts Python Taxonomy Parser
        """
        with SyncTransactionCtx() as session:
            # Create parser object and pass current session to it
            parser_object = parser.Parser(session)
            try:
                # Parse taxonomy with given file name and branch name
                parser_object(filepath, self.branch_name, self.taxonomy_name)
            except Exception as e:
                # outer exception handler will put project status to FAILED
                raise TaxonomyParsingError() from e

    async def get_and_parse_taxonomy(self, uploadfile: UploadFile | None = None):
        try:
            with tempfile.TemporaryDirectory(prefix="taxonomy-") as tmpdir:
                filepath = await (
                    self.get_github_taxonomy_file(tmpdir)
                    if uploadfile is None
                    else self.get_local_taxonomy_file(tmpdir, uploadfile)
                )
                await run_in_threadpool(self.parse_taxonomy, filepath)
                async with TransactionCtx():
                    await edit_project(self.project_name, ProjectEdit(status=ProjectStatus.OPEN))
        except Exception as e:
            # add an error node so we can display it with errors in the app
            async with TransactionCtx():
                await edit_project(self.project_name, ProjectEdit(status=ProjectStatus.FAILED))
            raise e

    async def import_taxonomy(
        self,
        description: str,
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
                is_from_github=uploadfile is None,
            )
        )
        background_tasks.add_task(self.get_and_parse_taxonomy, uploadfile)
        return True

    def dump_taxonomy(self, background_tasks: BackgroundTasks):
        """
        Helper function to create the txt file of a taxonomy
        """
        # Create unparser object and pass a sync session to it
        with SyncTransactionCtx() as session:
            unparser_object = unparser.WriteTaxonomy(session)
            # Creates a unique file for dumping the taxonomy
            filename = self.project_name + ".txt"
            try:
                # Dump taxonomy with given file name and branch name
                unparser_object(filename, self.branch_name, self.taxonomy_name)
                # Program file removal in the background
                background_tasks.add_task(file_cleanup, filename)
                return filename
            except Exception as e:
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
        is_from_github, status, description, commit_sha, file_sha, pr_url = (
            project.is_from_github,
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
            new_file = await github_object.update_file(filename, file_sha)

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

    async def create_project(self, description):
        """
        Helper function to create a node with label "PROJECT"
        """
        query = """
            CREATE (n:PROJECT)
            SET n.id = $project_name
            SET n.taxonomy_name = $taxonomy_name
            SET n.branch_name = $branch_name
            SET n.description = $description
            SET n.status = $status
            SET n.created_at = datetime()
        """
        params = {
            "project_name": self.project_name,
            "taxonomy_name": self.taxonomy_name,
            "branch_name": self.branch_name,
            "description": description,
            "status": "LOADING",
        }
        await get_current_transaction().run(query, params)

    async def get_project_info(self):
        """
        Helper function to get information about a Taxonomy Editor project
        """
        query = """
            MATCH (p:PROJECT {id: $project_name})
            RETURN p AS info
        """
        params = {"project_name": self.project_name}

        result = await get_current_transaction().run(query, params)  # returns a coroutine
        info_record = await result.single()
        info = info_record["info"] if info_record else None

        return info

    def set_project_status(self, session, status):
        """
        Helper function to update a Taxonomy Editor project status
        """
        query = """
            MATCH (n:PROJECT)
            WHERE n.id = $project_name
            SET n.status = $status
        """
        params = {"project_name": self.project_name, "status": status}
        with session.begin_transaction() as tx:
            tx.run(query, params)

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

    async def add_node_to_end(self, label, entry):
        """
        Helper function which adds an existing node to end of taxonomy
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
            MATCH (new_node:{self.project_name}:{label}) WHERE new_node.id = $id
            MATCH (last_node:{self.project_name}:{end_node_label}) WHERE last_node.id = $endnodeid
            MATCH (footer:{self.project_name}:TEXT) WHERE footer.id = "__footer__"
            CREATE (last_node)-[:is_before]->(new_node)
            CREATE (new_node)-[:is_before]->(footer)
        """
        await get_current_transaction().run(query, {"id": entry, "endnodeid": end_node["id"]})

    async def add_node_to_beginning(self, label, entry):
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
            MATCH (new_node:{self.project_name}:{label}) WHERE new_node.id = $id
            MATCH (first_node:{self.project_name}:{start_node_label})
                WHERE first_node.id = $startnodeid
            MATCH (header:{self.project_name}:TEXT) WHERE header.id = "__header__"
            CREATE (new_node)-[:is_before]->(first_node)
            CREATE (header)-[:is_before]->(new_node)
        """
        await get_current_transaction().run(query, {"id": entry, "startnodeid": start_node["id"]})

    async def delete_node(self, label, entry):
        """
        Helper function used for deleting a node with given id and label
        """
        # Finding node to be deleted using node ID
        query = f"""
            // Find node to be deleted using node ID
            MATCH (deleted_node:{self.project_name}:{label})-[:is_before]->(next_node)
                WHERE deleted_node.id = $id
            MATCH (previous_node)-[:is_before]->(deleted_node)
            // Remove node
            DETACH DELETE (deleted_node)
            // Rebuild relationships after deletion
            CREATE (previous_node)-[:is_before]->(next_node)
        """
        result = await get_current_transaction().run(query, {"id": entry})
        return await async_list(result)

    async def get_all_nodes(self, label):
        """
        Helper function used for getting all nodes with/without given label
        """
        qualifier = f":{label}" if label else ""
        query = f"""
            MATCH (n:{self.project_name}{qualifier}) RETURN n
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

    async def get_nodes(self, label, entry):
        """
        Helper function used for getting the node with given id and label
        """
        query = f"""
            MATCH (n:{self.project_name}:{label}) WHERE n.id = $id
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

    async def update_node(self, label, entry, new_node):
        """
        Helper function used for updation of node with given id and label
        """
        # Sanity check keys
        for key in new_node.keys():
            if not re.match(r"^\w+$", key) or key == "id":
                raise ValueError("Invalid key: %s", key)

        # Get current node information and deleted keys
        result = await self.get_nodes(label, entry)
        curr_node = result[0]["n"]
        deleted_keys = set(curr_node.keys()) - set(new_node.keys())

        # Check for keys having null/empty values
        for key in new_node.keys():
            if ((new_node[key] == []) or (new_node[key] is None)) and key != "preceding_lines":
                deleted_keys.add(key)
                # Delete tags_ids if we delete tags of a language
                if key.startswith("tags_") and "_ids_" not in key:
                    deleted_keys.add("tags_ids_" + key.split("_", 1)[1])

        # Build query
        query = [f"""MATCH (n:{self.project_name}:{label}) WHERE n.id = $id """]

        # Delete keys removed by user
        for key in deleted_keys:
            if key == "id":  # Doesn't require to be deleted
                continue
            query.append(f"""\nREMOVE n.{key}\n""")

        # Adding normalized tags ids corresponding to entry tags
        normalised_new_node = {}
        stopwords = await self.get_stopwords_dict()
        for key in set(new_node.keys()) - deleted_keys:
            if key.startswith("tags_"):
                if "_ids_" not in key:
                    keys_language_code = key.split("_", 1)[1]
                    normalised_value = []
                    for value in new_node[key]:
                        normalised_value.append(
                            parser_utils.normalize_text(
                                value, keys_language_code, stopwords=stopwords
                            )
                        )
                    normalised_new_node[key] = new_node[key]
                    normalised_new_node["tags_ids_" + keys_language_code] = normalised_value
                else:
                    pass  # We generate tags_ids, and ignore the one sent
            else:
                # No need to normalise
                normalised_new_node[key] = new_node[key]

        # Update keys
        for key in normalised_new_node.keys():
            query.append(f"""\nSET n.{key} = ${key}\n""")

        # Update id if first translation of the main language has changed
        main_language, id = curr_node["id"].split(":")
        new_normalised_first_translation = normalised_new_node["tags_ids_" + main_language][0]
        if id != new_normalised_first_translation:
            if (
                len(
                    await self.get_nodes(
                        label, f"{main_language}:{new_normalised_first_translation}"
                    )
                )
                != 0
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Entry {main_language}:{new_normalised_first_translation} already exists"
                    ),
                )
            normalised_new_node["new_id"] = main_language + ":" + new_normalised_first_translation
            query.append("""\nSET n.id = $new_id\n""")

        query.append("""RETURN n""")

        params = dict(normalised_new_node, id=entry)
        result = await get_current_transaction().run(" ".join(query), params)
        return (await async_list(result))[0]["n"]

    async def update_node_children(self, entry, new_children_ids):
        """
        Helper function used for updation of node children with given id
        """
        # Parse node ids from Neo4j Record object
        current_children = [record["child.id"] for record in list(await self.get_children(entry))]
        deleted_children = set(current_children) - set(new_children_ids)
        added_children = set(new_children_ids) - set(current_children)

        # Delete relationships
        for child in deleted_children:
            query = f"""
                MATCH
                    (deleted_child:{self.project_name}:ENTRY)
                    -[rel:is_child_of]->
                    (parent:{self.project_name}:ENTRY)
                WHERE parent.id = $id AND deleted_child.id = $child
                DELETE rel
            """
            await get_current_transaction().run(query, {"id": entry, "child": child})

        # Create non-existing nodes
        query = f"""
            MATCH (child:{self.project_name}:ENTRY)
                WHERE child.id in $ids RETURN child.id
        """
        _result = await get_current_transaction().run(query, ids=list(added_children))
        existing_ids = [record["child.id"] for record in (await _result.data())]
        to_create = added_children - set(existing_ids)

        # Normalising new children node ID
        created_child_ids = []

        for child in to_create:
            main_language_code = child.split(":", 1)[0]
            created_node_id = await self.create_node("ENTRY", child, main_language_code)
            created_child_ids.append(created_node_id)

            # TODO: We would prefer to add the node just after its parent entry
            await self.add_node_to_end("ENTRY", created_node_id)

        # Stores result of last query executed
        result = []
        children_ids = created_child_ids + existing_ids
        for child_id in children_ids:
            # Create new relationships if it doesn't exist
            query = f"""
                MATCH ()-[r:is_child_of]->(parent:{self.project_name}:ENTRY),
                (new_child:{self.project_name}:ENTRY)
                WHERE parent.id = $id AND new_child.id = $child_id
                WITH parent, new_child, COUNT(r) AS rel_count
                MERGE (new_child)-[r:is_child_of]->(parent)
                ON CREATE SET r.position = rel_count
            """
            _result = await get_current_transaction().run(
                query, {"id": entry, "child_id": child_id}
            )
            result = list(await _result.value())

        return result

    async def full_text_search(self, text):
        """
        Helper function used for searching a taxonomy
        """
        # Escape special characters
        normalized_text = re.sub(r"[^A-Za-z0-9_]", r" ", text)
        normalized_id_text = parser_utils.normalize_text(text)

        # If normalized text is empty, no searches are found
        if normalized_text.strip() == "":
            return []

        id_index = self.project_name + "_SearchIds"
        tags_index = self.project_name + "_SearchTags"

        text_query_exact = "*" + normalized_text + "*"
        text_query_fuzzy = normalized_text + "~"
        text_id_query_fuzzy = normalized_id_text + "~"
        text_id_query_exact = "*" + normalized_id_text + "*"
        params = {
            "id_index": id_index,
            "tags_index": tags_index,
            "text_query_fuzzy": text_query_fuzzy,
            "text_query_exact": text_query_exact,
            "text_id_query_fuzzy": text_id_query_fuzzy,
            "text_id_query_exact": text_id_query_exact,
        }

        # Fuzzy search and wildcard (*) search on two indexes
        # Fuzzy search has more priority, since it matches more close strings
        # IDs are given slightly lower priority than tags in fuzzy search
        query = """
            CALL {
                    CALL db.index.fulltext.queryNodes($id_index, $text_id_query_fuzzy)
                    yield node, score as score_
                    where score_ > 0
                    return node, score_ * 3 as score
                UNION
                    CALL db.index.fulltext.queryNodes($tags_index, $text_query_fuzzy)
                    yield node, score as score_
                    where score_ > 0
                    return node, score_ * 5 as score
                UNION
                    CALL db.index.fulltext.queryNodes($id_index, $text_id_query_exact)
                    yield node, score as score_
                    where score_ > 0
                    return node, score_ as score
                UNION
                    CALL db.index.fulltext.queryNodes($tags_index, $text_query_exact)
                    yield node, score as score_
                    where score_ > 0
                    return node, score_ as score
            }
            with node.id as node, score
            RETURN node, sum(score) as score

            ORDER BY score DESC
        """
        _result = await get_current_transaction().run(query, params)
        result = [record["node"] for record in await _result.data()]
        return result

    async def delete_taxonomy_project(self, branch, taxonomy_name):
        """
        Delete taxonomy projects
        """

        delete_query = """
            MATCH (n:PROJECT {taxonomy_name: $taxonomy_name, branch_name: $branch_name})
            DELETE n
        """
        result = await get_current_transaction().run(
            delete_query, taxonomy_name=taxonomy_name, branch_name=branch
        )
        summary = await result.consume()
        count = summary.counters.nodes_deleted
        return count
