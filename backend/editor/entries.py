"""
Database helper functions for API
"""
import re
import tempfile
import urllib.request  # Sending requests

from openfoodfacts_taxonomy_parser import normalizer  # Normalizing tags
from openfoodfacts_taxonomy_parser import parser  # Parser for taxonomies
from openfoodfacts_taxonomy_parser import unparser  # Unparser for taxonomies

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

        # Build all basic keys of a node
        if label == "ENTRY":
            # Normalizing new canonical tag
            language_code, canonical_tag = entry.split(":", 1)
            normalised_canonical_tag = normalizer.normalizing(canonical_tag, main_language_code)

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

    async def parse_taxonomy(self, filename):
        """
        Helper function to call the Open Food Facts Python Taxonomy Parser
        """
        # Close current transaction to use the session variable in parser
        await get_current_transaction().commit()

        with SyncTransactionCtx() as session:
            # Create parser object and pass current session to it
            parser_object = parser.Parser(session)
            try:
                # Parse taxonomy with given file name and branch name
                parser_object(filename, self.branch_name, self.taxonomy_name)
                return True
            except Exception as e:
                raise TaxonomyParsingError() from e

    async def import_from_github(self, description):
        """
        Helper function to import a taxonomy from GitHub
        """
        base_url = (
            "https://raw.githubusercontent.com/openfoodfacts/openfoodfacts-server"
            "/main/taxonomies/"
        )
        filename = self.taxonomy_name + ".txt"
        base_url += filename
        try:
            with tempfile.TemporaryDirectory(prefix="taxonomy-") as tmpdir:
                # File to save the downloaded taxonomy
                filepath = f"{tmpdir}/{filename}"

                # Downloads and creates taxonomy file in current working directory
                urllib.request.urlretrieve(base_url, filepath)

                status = await self.parse_taxonomy(filepath)  # Parse the taxonomy

            async with TransactionCtx():
                await self.create_project(description)  # Creates a "project node" in neo4j

            return status
        except Exception as e:
            raise TaxonomyImportError() from e

    async def upload_taxonomy(self, filepath, description):
        """
        Helper function to upload a taxonomy file and create a project node
        """
        try:
            status = await self.parse_taxonomy(filepath)
            async with TransactionCtx():
                await self.create_project(description)
            return status
        except Exception as e:
            raise TaxonomyImportError() from e

    def dump_taxonomy(self):
        """
        Helper function to create the txt file of a taxonomy
        """
        # Create unparser object and pass a sync session to it
        with SyncTransactionCtx() as session:
            unparser_object = unparser.WriteTaxonomy(session)
            # Creates a unique file for dumping the taxonomy
            filename = self.project_name + ".txt"
            try:
                # Parse taxonomy with given file name and branch name
                unparser_object(filename, self.branch_name, self.taxonomy_name)
                return filename
            except Exception as e:
                raise TaxonomyUnparsingError() from e

    async def file_export(self):
        """Export a taxonomy for download"""
        # Close current transaction to use the session variable in unparser
        await get_current_transaction().commit()

        filepath = self.dump_taxonomy()
        return filepath

    async def github_export(self):
        """Export a taxonomy to Github"""
        # Close current transaction to use the session variable in unparser
        await get_current_transaction().commit()

        filepath = self.dump_taxonomy()
        # Create a new transaction context
        async with TransactionCtx():
            result = await self.export_to_github(filepath)
            await self.set_project_status(status="CLOSED")
        return result

    async def export_to_github(self, filename):
        """
        Helper function to export a taxonomy to GitHub
        """
        query = """MATCH (n:PROJECT) WHERE n.id = $project_name RETURN n.description"""
        result = await get_current_transaction().run(query, {"project_name": self.project_name})
        description = (await result.data())[0]["n.description"]

        github_object = GithubOperations(self.taxonomy_name, self.branch_name)
        try:
            github_object.checkout_branch()
        except Exception as e:
            raise GithubBranchExistsError() from e
        try:
            github_object.update_file(filename)
            pr_object = github_object.create_pr(description)
            return (pr_object.html_url, filename)
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

    async def is_branch_unique(self):
        """
        Helper function to check uniqueness of GitHub branch
        """
        query = """MATCH (n:PROJECT) WHERE n.branch_name = $branch_name RETURN n"""
        result = await get_current_transaction().run(query, {"branch_name": self.branch_name})

        github_object = GithubOperations(self.taxonomy_name, self.branch_name)
        current_branches = github_object.list_all_branches()

        if (await result.value() == []) and (self.branch_name not in current_branches):
            return True
        else:
            return False

    def is_valid_branch_name(self):
        """
        Helper function to check if a branch name is valid
        """
        return normalizer.normalizing(self.branch_name, char="_") == self.branch_name

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
            "status": "OPEN",
        }
        await get_current_transaction().run(query, params)

    async def set_project_status(self, status):
        """
        Helper function to update a Taxonomy Editor project status
        """
        query = """
            MATCH (n:PROJECT)
            WHERE n.id = $project_name
            SET n.status = $status
        """
        params = {"project_name": self.project_name, "status": status}
        await get_current_transaction().run(query, params)

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

    async def update_nodes(self, label, entry, new_node_keys):
        """
        Helper function used for updation of node with given id and label
        """
        # Sanity check keys
        for key in new_node_keys.keys():
            if not re.match(r"^\w+$", key) or key == "id":
                raise ValueError("Invalid key: %s", key)

        # Get current node information and deleted keys
        result = await self.get_nodes(label, entry)
        curr_node = result[0]["n"]
        curr_node_keys = list(curr_node.keys())
        deleted_keys = set(curr_node_keys) ^ set(new_node_keys)

        # Check for keys having null/empty values
        for key in curr_node_keys:
            if (curr_node[key] == []) or (curr_node[key] is None):
                deleted_keys.add(key)

        # Build query
        query = [f"""MATCH (n:{self.project_name}:{label}) WHERE n.id = $id """]

        # Delete keys removed by user
        for key in deleted_keys:
            if key == "id":  # Doesn't require to be deleted
                continue
            query.append(f"""\nREMOVE n.{key}\n""")

        # Adding normalized tags ids corresponding to entry tags
        normalised_new_node_keys = {}
        for keys in new_node_keys.keys():
            if keys.startswith("tags_"):
                if "_ids_" not in keys:
                    keys_language_code = keys.split("_", 1)[1]
                    normalised_value = []
                    for values in new_node_keys[keys]:
                        normalised_value.append(normalizer.normalizing(values, keys_language_code))
                    normalised_new_node_keys[keys] = normalised_value
                    normalised_new_node_keys["tags_ids_" + keys_language_code] = normalised_value
                else:
                    pass  # We generate tags_ids, and ignore the one sent
            else:
                # No need to normalise
                normalised_new_node_keys[keys] = new_node_keys[keys]

        # Update keys
        for key in normalised_new_node_keys.keys():
            query.append(f"""\nSET n.{key} = ${key}\n""")

        query.append("""RETURN n""")

        params = dict(normalised_new_node_keys, id=entry)
        result = await get_current_transaction().run(" ".join(query), params)
        return await async_list(result)

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
                MATCH (parent:{self.project_name}:ENTRY), (new_child:{self.project_name}:ENTRY)
                WHERE parent.id = $id AND new_child.id = $child_id
                MERGE (new_child)-[r:is_child_of]->(parent)
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
        normalized_id_text = normalizer.normalizing(text)

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
