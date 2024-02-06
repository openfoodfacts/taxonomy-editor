import collections
import logging
import os
import sys
import timeit

import iso639
from neo4j import GraphDatabase, Session, Transaction

from .logger import ParserConsoleLogger
from ..utils import get_project_name, normalize_text
from .taxonomy_parser import (
    NodeType,
    PreviousLink,
    Taxonomy,
    TaxonomyParser,
    NodeData,
    ChildLink,
)


class Parser:
    """Parse a taxonomy file and build a neo4j graph"""

    def __init__(self, session: Session):
        self.session = session
        self.parser_logger = ParserConsoleLogger()

    def _create_other_node(self, tx: Transaction, node_data: NodeData, project_label: str):
        """Create a TEXT, SYNONYMS or STOPWORDS node"""
        if node_data.get_node_type() == NodeType.TEXT:
            type_label = "TEXT"
        elif node_data.get_node_type() == NodeType.SYNONYMS:
            type_label = "SYNONYMS"
        elif node_data.get_node_type() == NodeType.STOPWORDS:
            type_label = "STOPWORDS"
        else:
            raise ValueError(f"ENTRY nodes should not be passed to this function")

        node_tags_queries = [f"{key} : ${key}" for key in node_data.tags]

        base_properties_query = """
            id: $id,
            preceding_lines: $preceding_lines,
            src_position: $src_position
        """

        properties_query = ",\n".join([base_properties_query, *node_tags_queries])

        query = f"""
            CREATE (n:{project_label}:{type_label} {{ {properties_query} }})
        """
        tx.run(query, node_data.to_dict())

    def _create_other_nodes(self, other_nodes: list[NodeData], project_label: str):
        """Create all TEXT, SYNONYMS and STOPWORDS nodes"""
        self.parser_logger.info("Creating TEXT, SYNONYMS and STOPWORDS nodes")
        start_time = timeit.default_timer()

        with self.session.begin_transaction() as tx:
            for node in other_nodes:
                self._create_other_node(tx, node, project_label)

        self.parser_logger.info(
            f"Created {len(other_nodes)} TEXT, SYNONYMS and STOPWORDS nodes in {timeit.default_timer() - start_time} seconds"
        )

    def _create_entry_nodes(self, entry_nodes: list[NodeData], project_label: str):
        """Create all ENTRY nodes in a single batch query"""
        self.parser_logger.info("Creating ENTRY nodes")
        start_time = timeit.default_timer()

        # we don't know in advance which properties and tags
        # we will encounter in the batch
        # so we accumulate them in this set
        seen_properties_and_tags = set()

        for entry_node in entry_nodes:
            if entry_node.get_node_type() != NodeType.ENTRY:
                raise ValueError(f"Only ENTRY nodes should be passed to this function")
            seen_properties_and_tags.update(entry_node.tags)
            seen_properties_and_tags.update(entry_node.properties)

        additional_properties_queries = [
            f"{key} : entry_node.{key}" for key in seen_properties_and_tags
        ]

        base_properties_query = f"""
            id: entry_node.id,
            preceding_lines: entry_node.preceding_lines,
            src_position: entry_node.src_position,
            main_language: entry_node.main_language
        """

        properties_query = ",\n".join([base_properties_query, *additional_properties_queries])

        query = f"""
          WITH $entry_nodes as entry_nodes
          UNWIND entry_nodes as entry_node
          CREATE (n:{project_label}:ENTRY {{ {properties_query} }})
        """
        self.session.run(query, entry_nodes=[entry_node.to_dict() for entry_node in entry_nodes])

        self.parser_logger.info(
            f"Created {len(entry_nodes)} ENTRY nodes in {timeit.default_timer() - start_time} seconds"
        )

    def _create_previous_links(self, previous_links: list[PreviousLink], project_label: str):
        """Create the 'is_before' relations between nodes"""
        self.parser_logger.info("Creating 'is_before' links")
        start_time = timeit.default_timer()

        # The previous links creation is batched in a single query
        # We also use the ID index to speed up the MATCH queries
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

        self.parser_logger.info(
            f"Created {count} 'is_before' links in {timeit.default_timer() - start_time} seconds"
        )

        if count != len(previous_links):
            self.parser_logger.error(
                f"Created {count} 'is_before' links, {len(previous_links)} links expected"
            )

    def _create_child_links(
        self, child_links: list[ChildLink], project_label: str
    ):
        """Create the 'is_child_of' relations between nodes"""
        self.parser_logger.info("Creating 'is_child_of' links")
        start_time = timeit.default_timer()

        query = (
            f"""
                UNWIND $child_links as child_link
                MATCH (p:{project_label}) USING INDEX p:{project_label}(id)
                WHERE p.id = child_link.parent_id
                MATCH (c:{project_label}) USING INDEX c:{project_label}(id)
            """
            + """
                WHERE c.id = child_link.id
                CREATE (c)-[relations:is_child_of {position: child_link.position}]->(p)
                WITH relations
                UNWIND relations AS relation
                RETURN COUNT(relation)
            """
        )

        normalised_result = self.session.run(
            query, child_links=child_links
        )
        count = normalised_result.value()[0]

        self.parser_logger.info(
            f"Created {count} 'is_child_of' links in {timeit.default_timer() - start_time} seconds"
        )

        if count != len(child_links):
            self.parser_logger.error(
                f"Created {count} 'is_child_of' links, {len(child_links)} links expected"
            )

    def _create_parsing_errors_node(self, taxonomy_name: str, branch_name: str, project_label: str):
        """Create node to list parsing errors"""
        self.parser_logger.info("Creating 'ERRORS' node")
        start_time = timeit.default_timer()

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

        self.parser_logger.info(
            f"Created 'ERRORS' node in {timeit.default_timer() - start_time} seconds"
        )

    def _create_node_id_index(self, project_label: str):
        """Create index for search query optimization"""
        query = f"""
            CREATE INDEX {project_label}_id_index IF NOT EXISTS FOR (n:{project_label}) ON (n.id)
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
        """Create node indexes"""
        self.parser_logger.info("Creating indexes")
        start_time = timeit.default_timer()

        self._create_node_id_index(project_label)
        self._create_node_fulltext_index(project_label)

        self.parser_logger.info(f"Created indexes in {timeit.default_timer() - start_time} seconds")

    def _write_to_database(self, taxonomy: Taxonomy, taxonomy_name: str, branch_name: str):
        project_label = get_project_name(taxonomy_name, branch_name)
        # First create nodes, then create node indexes to accelerate relationship creation, then create relationships
        self._create_other_nodes(taxonomy.other_nodes, project_label)
        self._create_entry_nodes(taxonomy.entry_nodes, project_label)
        self._create_node_indexes(project_label)
        self._create_child_links(taxonomy.child_links, project_label)
        self._create_previous_links(taxonomy.previous_links, project_label)
        # Lastly create the parsing errors node
        self._create_parsing_errors_node(taxonomy_name, branch_name, project_label)

    def __call__(self, filename: str, branch_name: str, taxonomy_name: str):
        """Process the file"""
        start_time = timeit.default_timer()

        branch_name = normalize_text(branch_name, char="_")
        taxonomy_parser = TaxonomyParser()
        taxonomy = taxonomy_parser.parse_file(filename, self.parser_logger)
        self._write_to_database(taxonomy, taxonomy_name, branch_name)

        self.parser_logger.info(
            f"Finished parsing {taxonomy_name} in {timeit.default_timer() - start_time} seconds"
        )


if __name__ == "__main__":
    # Setup logs
    logging.basicConfig(handlers=[logging.StreamHandler()], level=logging.INFO)
    filename = sys.argv[1] if len(sys.argv) > 1 else "test"
    branch_name = sys.argv[2] if len(sys.argv) > 1 else "branch"
    taxonomy_name = sys.argv[3] if len(sys.argv) > 1 else filename.rsplit(".", 1)[0]

    # Initialize neo4j
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    driver = GraphDatabase.driver(uri)
    session = driver.session(database="neo4j")

    # Pass session variable to parser object
    parse = Parser(session)
    parse(filename, branch_name, taxonomy_name)
