import logging
import os
import sys

import iso639
from neo4j import GraphDatabase, Session, Transaction

from .logger import ParserConsoleLogger
from ..normalizer import normalizing
from .taxonomy_parser import (
    NodeType,
    PreviousLink,
    Taxonomy,
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

    def _create_other_node(self, node_data: NodeData, project_label: str):
        """Create TEXT, SYNONYMS or STOPWORDS nodes"""
        position_query = """
            SET n.id = $id
            SET n.preceding_lines = $preceding_lines
            SET n.src_position = $src_position
        """
        if node_data.get_node_type() == NodeType.TEXT:
            id_query = f" CREATE (n:{project_label}:TEXT) \n "
        elif node_data.get_node_type() == NodeType.SYNONYMS:
            id_query = f" CREATE (n:{project_label}:SYNONYMS) \n "
        elif node_data.get_node_type() == NodeType.STOPWORDS:
            id_query = f" CREATE (n:{project_label}:STOPWORDS) \n "
        else:
            raise ValueError(f"ENTRY node type should be batched")

        entry_query = ""
        for key in node_data.tags:
            entry_query += " SET n." + key + " = $" + key + "\n"

        query = id_query + entry_query + position_query
        tx.run(query, node_data.to_dict())

    def _create_entry_nodes(self, entry_nodes: list[NodeData], project_label: str):
        """Create all ENTRY nodes in a single batch query"""
        base_query = f"""
          WITH $entry_nodes as entry_nodes
          UNWIND entry_nodes as entry_node
          CREATE (n:{project_label}:ENTRY)
          SET n.id = entry_node.id
          SET n.preceding_lines = entry_node.preceding_lines
          SET n.src_position = entry_node.src_position
          SET n.main_language = entry_node.main_language
        """
        additional_query = ""
        seen_properties = set()
        seen_tags = set()
        for entry_node in entry_nodes:
            if entry_node.get_node_type() != NodeType.ENTRY:
                raise ValueError(f"Only ENTRY nodes can be batched")
            for key in entry_node.properties:
                if not key in seen_properties:
                    additional_query += " SET n." + key + " = entry_node." + key + "\n"
                    seen_properties.add(key)
            for key in entry_node.tags:
                if not key in seen_tags:
                    additional_query += " SET n." + key + " = entry_node." + key + "\n"
                    seen_tags.add(key)

        query = base_query + additional_query
        self.session.run(query, entry_nodes=[entry_node.to_dict() for entry_node in entry_nodes])

    def _create_other_nodes(self, other_nodes: list[NodeData], project_label: str):
        with self.session.begin_transaction() as tx:
            for node in other_nodes:
                self._create_other_node(tx, node, project_label)

    def _create_previous_links(self, previous_links: list[PreviousLink], project_label: str):
        self.parser_logger.info("Creating 'is_before' links")
        query = f"""
            UNWIND $previous_links as previous_link
            MATCH(n:{project_label}) USING INDEX n:{project_label}(id)
            WHERE n.id = previous_link.id
            MATCH(p:{project_label}) USING INDEX p:{project_label}(id)
            WHERE p.id = previous_link.before_id
            CREATE (p)-[relations:is_before]->(n)
            WITH relations
            UNWIND relations AS relation
            RETURN COUNT(relation)
        """
        result = self.session.run(query, previous_links=previous_links)

        count = result.value()[0]
        if count != len(previous_links):
            self.parser_logger.error(
                "Created %s 'is_before' links, %s links expected", count, len(previous_links)
            )

    def _create_child_links(
        self, child_links: list[ChildLink], entry_nodes: list[NodeData], project_label: str
    ):
        """Create the relations between nodes"""
        self.parser_logger.info("Creating 'is_child_of' links")
        node_ids = set([node.id for node in entry_nodes])
        normalised_child_links = []
        unnormalised_child_links = []
        for child_link in child_links:
            if child_link["parent_id"] in node_ids:
                normalised_child_links.append(child_link)
            else:
                unnormalised_child_links.append(child_link)

        normalised_query = f"""
            UNWIND $normalised_child_links as child_link
            MATCH (p:{project_label}) USING INDEX p:{project_label}(id)
            WHERE p.id = child_link.parent_id
            MATCH (c:{project_label}) USING INDEX c:{project_label}(id)
            WHERE c.id = child_link.id
            CREATE (c)-[relations:is_child_of]->(p)
            WITH relations
            UNWIND relations AS relation
            RETURN COUNT(relation)
        """

        language_codes = set()
        for child_link in unnormalised_child_links:
            lc, parent_id = child_link["parent_id"].split(":")
            language_codes.add(lc)
            child_link["parent_id"] = parent_id

        parent_id_query = " OR ".join(
            [f"child_link.parent_id IN p.tags_ids_{lc}" for lc in language_codes]
        )

        unnormalised_query = f"""
            UNWIND $unnormalised_child_links as child_link
            MATCH (p:{project_label})
            WHERE {parent_id_query}
            MATCH (c:{project_label}) USING INDEX c:{project_label}(id)
            WHERE c.id = child_link.id
            CREATE (c)-[relations:is_child_of]->(p)
            WITH relations
            UNWIND relations AS relation
            RETURN COUNT(relation)
        """
        count = 0

        if normalised_child_links:
            normalised_result = self.session.run(
                normalised_query, normalised_child_links=normalised_child_links
            )
            count += normalised_result.value()[0]

        if unnormalised_child_links:
            unnormalised_result = self.session.run(
                unnormalised_query, unnormalised_child_links=unnormalised_child_links
            )
            count += unnormalised_result.value()[0]
        

        if count != len(child_links):
            self.parser_logger.error(
                "Created %s 'is_child_of' links, %s links expected",
                count,
                len(child_links),
            )

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

    def _create_node_id_index(self, project_label: str):
        """Create index for search query optimization"""
        query = f"""
            CREATE INDEX {project_label}_id_index FOR (n:{project_label}) ON (n.id)
        """
        self.session.run(query)

    def _create_node_fulltext_index(self, project_label: str):
        """Create indexes for text search"""
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

    def _create_node_indexes(self, project_label: str):
        self._create_node_id_index(project_label)
        self._create_node_fulltext_index(project_label)

    def _write_to_database(self, taxonomy: Taxonomy, taxonomy_name: str, branch_name: str):
        project_label = self._get_project_name(taxonomy_name, branch_name)
        self._create_other_nodes(taxonomy.other_nodes, project_label)
        self._create_entry_nodes(taxonomy.entry_nodes, project_label)
        self._create_node_indexes(project_label)
        self._create_child_links(taxonomy.child_links, taxonomy.entry_nodes, project_label)
        self._create_previous_links(taxonomy.previous_links, project_label)
        self._create_parsing_errors_node(taxonomy_name, branch_name, project_label)

    def __call__(self, filename: str, branch_name: str, taxonomy_name: str):
        """Process the file"""
        branch_name = normalizing(branch_name, char="_")
        taxonomy_parser = TaxonomyParser()
        taxonomy = taxonomy_parser.parse_file(filename, self.parser_logger)
        self._write_to_database(taxonomy, taxonomy_name, branch_name)

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
