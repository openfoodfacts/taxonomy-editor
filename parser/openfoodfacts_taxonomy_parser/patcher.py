"""This module provide a function to dump a taxonomy from a neo4j database into a file,
but taking the original taxonomy content and only modifying nodes that where modified or added
"""

from collections import defaultdict

from .unparser import WriteTaxonomy
from .utils import get_project_name, src_lines


class PatchTaxonomy(WriteTaxonomy):
    """Implementation to dump a taxonomy from neoo4j database into a file,
    while taking the original content and
    only modifying lines corresponding to nodes that where modified or added
    """

    def is_removed(self, node):
        return any(label.startswith("REMOVED") for label in node.labels)

    def get_all_nodes(self, project_label):
        """Get modified and removed nodes, in the start line  order"""
        query = f"""
            MATCH (n:({project_label}|REMOVED_{project_label}))
            WHERE
                // no external node
                (n.is_external = false OR n.is_external IS NULL)
                AND (
                    // modified nodes
                    ((n:TEXT OR n:SYNONYMS OR n:STOPWORDS OR n:ENTRY) AND n.modified IS NOT NULL)
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
        query = """
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
        original_text = self.get_original_text(branch_name, taxonomy_name)
        # get lines to replace and put them in a dict with the line number
        nodes_by_lines = self.nodes_by_lines(branch_name, taxonomy_name)
        # get lines to skip in original text
        skip_lines = {
            num_line
            for pairs in nodes_by_lines.values()
            for node, _ in pairs
            # note that for new nodes src_lines
            # is empty and that's what we want (no line to skip)
            for start, end in src_lines(node["src_lines"])
            # line 1 is 1, not 0, so slide of 1, and put every lines
            # we also add the following blank line in case of removed item
            for num_line in range(start - 1, end + (1 if self.is_removed(node) else 0))
        }
        previous_line = None
        node = None
        for line_num, line in enumerate(original_text.split("\n")):
            if line_num in nodes_by_lines:
                node_parents_list = nodes_by_lines.pop(line_num)
                for node, parents in node_parents_list:
                    if not self.is_removed(node):
                        node_lines = list(self.iter_node_lines(dict(node), parents))
                        if previous_line != "":
                            # we need a blank line between 2 nodes
                            yield ""
                        yield from node_lines
                        previous_line = node_lines[-1]
            # this is not a elif, because previous entry might not replace content (new entry)
            if line_num in skip_lines:
                continue
            else:
                yield line
                previous_line = line
        # add remaining nodes
        if not previous_line == "" and nodes_by_lines:
            yield ""
        for node_parents in nodes_by_lines.values():
            for node, parents in node_parents:
                yield from self.iter_node_lines(dict(node), parents)
                yield ""

    def nodes_by_lines(
        self, branch_name, taxonomy_name
    ) -> dict[int, list[tuple[dict, list[dict]]]]:
        """Get the lines to replace in the original text

        :return: dict association each line number
          with a list of nodes to put at this line
          as a tuple (node, parents)
        """
        project_label = get_project_name(taxonomy_name, branch_name)
        # get nodes by future position in the file
        nodes_by_lines = defaultdict(list)
        nodes_without_position = []
        # first pass for the easy ones
        for node, parents in self.get_all_nodes(project_label):
            node_position = node["src_position"]
            if not node_position:
                # this is a new node
                # we try to add it nearby it's latest parent,
                # if it's not possible, we add it at the end
                parents_with_position = filter(lambda x: x["src_position"] is not None, parents)
                parents_positions = sorted(parents_with_position, key=lambda x: x["src_position"])
                if parents_positions:
                    node_position = int(parents_positions[-1]["src_lines"][-1].split(",")[-1])
                elif parents:
                    nodes_without_position.append((node, parents))
                else:
                    # put at the end
                    node_position = -1
            if node_position:
                nodes_by_lines[node_position].append((node, parents))
        # we now try to see iteratively to see in nodes_without position
        # if node parents have acquired a position
        ids_positions = {
            node["id"]: node_position
            for node_position, nodes in nodes_by_lines.items()
            for node, _ in nodes
        }
        while True:
            position_found = []
            for i, (node, parents) in enumerate(nodes_without_position):
                candidates = set(parent["id"] for parent in parents) & set(ids_positions.keys())
                if candidates:
                    node_position = max(ids_positions[parent_id] for parent_id in candidates)
                    nodes_by_lines[node_position].append((node, parents))
                    position_found.append(i)
            if not position_found:
                break  # no more progress, we are done
            for i in reversed(position_found):
                del nodes_without_position[i]
        # put the rest at the end
        if nodes_without_position:
            nodes_by_lines[-1].extend(nodes_without_position)
        return nodes_by_lines
