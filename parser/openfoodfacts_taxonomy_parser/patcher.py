"""This module provide a function to dump a taxonomy from a neo4j database into a file,
but taking the original taxonomy content and only modifying nodes that where modified or added
"""

from .unparser import WriteTaxonomy
from .utils import get_project_name, src_lines


class PatchTaxonomy(WriteTaxonomy):
    """Implementation to dump a taxonomy from neoo4j database into a file,
    while taking the original content and
    only modifying lines corresponding to nodes that where modified or added
    """

    def get_all_nodes(self, project_label):
        """Get modified and removed nodes, in the start line  order"""
        query = f"""
            MATCH (n:{project_label})
            WHERE
                // no external node
                n.is_external = false
                AND (
                    // modified nodes
                    ((n:TEXT OR n:SYNONYMS OR n:STOPWORDS OR n:ENTRY) AND n.modified IS NOT NULL) OR
                    // removed nodes
                    (n:REMOVED_TEXT OR n:REMOVED_SYNONYMS OR n:REMOVED_STOPWORDS OR n:REMOVED_ENTRY)
                )
            // optional match for node might not have parents
            OPTIONAL
                MATCH (n)-[r:is_child_of]->(parent)
                WITH n, r, parent ORDER BY n.src_position, r.position
            RETURN n, collect(parent)
        """
        results = self.session.run(query)
        for result in results:
            node, parents = result.values()
            yield node, parents

    def get_original_text(self, branch_name, taxonomy_name):
        """Get the original text of the taxonomy"""
        query = f"""
            MATCH (n:PROJECT)
            WHERE n.branch_name = $branch_name AND n.taxonomy_name = $taxonomy_name
            RETURN n.original_text
        """
        results = self.session.run(
            query, {"branch_name": branch_name, "taxonomy_name": taxonomy_name}
        )
        for result in results:
            return result.values()[0]

    def iter_lines(self, branch_name, taxonomy_name):
        nodes_by_lines = self.nodes_by_lines(branch_name, taxonomy_name)
        # get lines to replace and put them in a dict with the line number
        original_text = self.get_original_text(branch_name, taxonomy_name)
        nodes_by_lines = self.nodes_by_lines(branch_name, taxonomy_name)
        # get lines to skip in original text
        skip_lines = {
            num_line
            for node, _ in nodes_by_lines.values()
            for start, end in src_lines(node.src_lines)
            for num_line in range(start, end)
        }
        previous_line = None
        for line_num, line in enumerate(original_text.split("\n")):
            if line_num in nodes_by_lines and not node.labels.startswith("REMOVED"):
                if previous_line != "":
                    # we need a blank line between 2 nodes
                    yield ""
                node, parents = nodes_by_lines.pop(line_num)
                node_lines = list(self.iter_node_lines(dict(node), parents))
                yield from lines
                previous_line = lines[-1]
            # this is not a elif, because previous entry might not replace content (new entry)
            if line_num in skip_lines:
                continue
            else:
                yield line
                previous_line = line
        # add remaining nodes
        if not previous_line == "" and nodes_by_lines:
            yield ""
        for node, parents in nodes_by_lines.values():
            yield from self.iter_node_lines(dict(node), parents)
            yield ""

    def nodes_by_lines(self, branch_name, taxonomy_name):
        """Get the lines to replace in the original text"""
        project_label = get_project_name(taxonomy_name, branch_name)
        # get nodes by future position in the file
        nodes_by_lines = {}
        new_lines = -1  # we will use negative positions to add new nodes at the end
        for node, parents in self.get_all_nodes(project_label):
            node_position = node.src_position
            if not node_position:
                # this is a new node
                # we try to add it nearby it's latest parent, if it's not possible, we add it at the end
                parents_with_position = filter(lambda x: x.src_position is not None, parents)
                parents_positions = sorted(parents_with_position, key=lambda x: x.src_position)
                if parents_positions:
                    node_position = int(parents_positions[-1].src_lines[-1][-1].split(",")[-1])
                else:
                    node_position = new_lines
                    new_lines -= 1
            nodes_by_lines[node_position] = (node, parents)
        return nodes_by_lines
