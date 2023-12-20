import logging
import os
import sys

import iso639
from neo4j import GraphDatabase, Session

from .logger import ParserConsoleLogger
from ..normalizer import normalizing
from .taxonomy_parser import (
    NodeType,
    PreviousLink,
    TaxonomyParser,
    NodeData,
    ChildLink,
)


def ellipsis(text, max=20):
    """Cut a text adding eventual ellipsis if we do not display it fully"""
    return text[:max] + ("..." if len(text) > max else "")


class Parser:
    """Parse a taxonomy file and build a neo4j graph"""

    def __init__(self, session: Session):
        self.session = session
        self.parser_logger = ParserConsoleLogger()

    def _get_project_name(self, taxonomy_name: str, branch_name: str):
        """Create a project name for given branch and taxonomy"""
        return "p_" + taxonomy_name + "_" + branch_name

    def _create_headernode(self, header: list[str], project_label: str):
        """Create the node for the header"""
        query = f"""
                CREATE (n:{project_label}:TEXT)
                SET n.id = '__header__'
                SET n.preceding_lines= $header
                SET n.src_position= 1
            """
        self.session.run(query, header=header)

    def _create_node(self, node_data: NodeData, project_label: str):
        """Run the query to create the node with data dictionary"""
        position_query = """
            SET n.id = $id
            SET n.is_before = $is_before
            SET n.preceding_lines = $preceding_lines
            SET n.src_position = $src_position
        """
        entry_query = ""
        if node_data.get_node_type() == NodeType.TEXT:
            id_query = f" CREATE (n:{project_label}:TEXT) \n "
        elif node_data.get_node_type() == NodeType.SYNONYMS:
            id_query = f" CREATE (n:{project_label}:SYNONYMS) \n "
        elif node_data.get_node_type() == NodeType.STOPWORDS:
            id_query = f" CREATE (n:{project_label}:STOPWORDS) \n "
        else:
            id_query = f" CREATE (n:{project_label}:ENTRY) \n "
            position_query += " SET n.main_language = $main_language "
            if node_data.parent_tag:
                entry_query += " SET n.parents = $parent_tag \n"
            for key in node_data.properties:
                if key.startswith("prop_"):
                    entry_query += " SET n." + key + " = $" + key + "\n"

        for key in node_data.tags:
            if key.startswith("tags_"):
                entry_query += " SET n." + key + " = $" + key + "\n"

        query = id_query + entry_query + position_query
        self.session.run(query, node_data.to_dict())

    def create_nodes(self, nodes: list[NodeData], project_label: str):
        """Adding nodes to database"""
        self.parser_logger.info("Creating nodes")
        for node in nodes:
            if node.id == "__header__":
                self._create_headernode(node.preceding_lines, project_label)
            else:
                self._create_node(node, project_label)

    def create_previous_link(self, previous_links: list[PreviousLink], project_label: str):
        self.parser_logger.info("Creating 'is_before' links")
        for previous_link in previous_links:
            id = previous_link["id"]
            before_id = previous_link["before_id"]

            query = f"""
                MATCH(n:{project_label}) WHERE n.id = $id
                MATCH(p:{project_label}) WHERE p.id= $before_id
                CREATE (p)-[r:is_before]->(n)
                RETURN r
            """
            results = self.session.run(query, id=id, before_id=before_id)
            relation = results.values()
            if len(relation) > 1:
                self.parser_logger.error(
                    "2 or more 'is_before' links created for ids %s and %s, "
                    "one of the ids isn't unique",
                    id,
                    before_id,
                )
            elif not relation[0]:
                self.parser_logger.error("link not created between %s and %s", id, before_id)

    def create_child_link(self, child_links: list[ChildLink], project_label: str):
        """Create the relations between nodes"""
        self.parser_logger.info("Creating 'is_child_of' links")
        for child_link in child_links:
            child_id = child_link["id"]
            parent = child_link["parent_id"]
            lc, parent_id = parent.split(":")
            query = f""" MATCH (p:{project_label}:ENTRY) WHERE $parent_id IN p.tags_ids_""" + lc
            query += f"""
                MATCH (c:{project_label}) WHERE c.id= $child_id
                CREATE (c)-[r:is_child_of]->(p)
                RETURN r
            """
            result = self.session.run(query, parent_id=parent_id, child_id=child_id)
            if not result.value():
                self.parser_logger.warning(
                    f"parent not found for child {child_id} with parent {parent_id}"
                )

    def _create_fulltext_index(self, project_label: str):
        """Create indexes for search"""
        query = (
            f"""CREATE FULLTEXT INDEX {project_label+'_SearchIds'} IF NOT EXISTS
            FOR (n:{project_label}) ON EACH [n.id]\n"""
            + """
            OPTIONS {indexConfig: {`fulltext.analyzer`: 'keyword'}}"""
        )
        self.session.run(query)

        language_codes = [lang.alpha2 for lang in list(iso639.languages) if lang.alpha2 != ""]
        tags_prefixed_lc = ["n.tags_" + lc for lc in language_codes]
        tags_prefixed_lc = ", ".join(tags_prefixed_lc)
        query = f"""CREATE FULLTEXT INDEX {project_label+'_SearchTags'} IF NOT EXISTS
            FOR (n:{project_label}) ON EACH [{tags_prefixed_lc}]"""
        self.session.run(query)

    def _create_parsing_errors_node(self, taxonomy_name: str, branch_name: str, project_label: str):
        """Create node to list parsing errors"""
        query = f"""
            CREATE (n:{project_label}:ERRORS)
            SET n.id = $project_name
            SET n.branch_name = $branch_name
            SET n.taxonomy_name = $taxonomy_name
            SET n.created_at = datetime()
            SET n.warnings = $warnings_list
            SET n.errors = $errors_list
        """
        params = {
            "project_name": project_label,
            "branch_name": branch_name,
            "taxonomy_name": taxonomy_name,
            "warnings_list": self.parser_logger.parsing_warnings,
            "errors_list": self.parser_logger.parsing_errors,
        }
        self.session.run(query, params)

    def __call__(self, filename: str, branch_name: str, taxonomy_name: str):
        """Process the file"""
        branch_name = normalizing(branch_name, char="_")
        project_label = self._get_project_name(taxonomy_name, branch_name)
        taxonomy_parser = TaxonomyParser()
        taxonomy = taxonomy_parser.parse_file(filename, self.parser_logger)
        self.create_nodes([*taxonomy.entry_nodes, *taxonomy.other_nodes], project_label)
        self.create_child_link(taxonomy.child_links, project_label)
        self.create_previous_link(taxonomy.previous_links, project_label)
        self._create_fulltext_index(project_label)
        self._create_parsing_errors_node(taxonomy_name, branch_name, project_label)


if __name__ == "__main__":
    # Setup logs
    logging.basicConfig(handlers=[logging.StreamHandler()], level=logging.INFO)
    filename = sys.argv[1] if len(sys.argv) > 1 else "test"
    branch_name = sys.argv[2] if len(sys.argv) > 1 else "branch"
    taxonomy_name = sys.argv[3] if len(sys.argv) > 1 else filename.rsplit(".", 1)[0]

    # Initialize neo4j
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    driver = GraphDatabase.driver(uri)
    session = driver.session()

    # Pass session variable to parser object
    parse = Parser(session)
    parse(filename, branch_name, taxonomy_name)
