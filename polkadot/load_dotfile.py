from dataclasses import dataclass
from typing import Dict, List, Optional

import pydot

DOT_RESERVED_NODE_IDS = frozenset({r'"\n"', "graph", "node", "edge", ""})
CHARS_TO_STRIP = "\\\r\n\t '\"<>"
NodeId = str
URL = str
Expected = str


@dataclass
class PolkadotNode:
    node_id: NodeId
    url: Optional[URL] = None
    expected: Optional[Expected] = None
    subgraph: Optional[str] = None


DotFile = str


def collect(
    g: pydot.Graph,
    node_id_to_nodes: Optional[Dict[NodeId, PolkadotNode]],
    subgraph_name: str = "",
) -> Dict[NodeId, PolkadotNode]:

    if node_id_to_nodes is None:
        node_id_to_nodes = dict()

    for node in g.get_nodes():
        node_id_orig = node.get_name()
        node_id = node_id_orig.strip(CHARS_TO_STRIP)
        if node_id in DOT_RESERVED_NODE_IDS or node_id_orig in DOT_RESERVED_NODE_IDS:
            continue
        attrs = {k.lower(): v for k, v in node.get_attributes().items()}
        url = attrs.get("url", None)
        if url is not None:
            url = url.strip(CHARS_TO_STRIP)

        expected = attrs.get("expected", None)
        if expected is not None:
            expected = expected.strip(CHARS_TO_STRIP).replace(r"\"", '"')

        pdn = PolkadotNode(node_id, url, expected, subgraph_name)
        node_id_to_nodes[node_id] = pdn

    for edge in g.get_edges():
        src = edge.get_source()
        dst = edge.get_destination()
        if src not in node_id_to_nodes:
            node_id_to_nodes[src] = PolkadotNode(src, subgraph=subgraph_name)
        if dst not in node_id_to_nodes:
            node_id_to_nodes[dst] = PolkadotNode(dst, subgraph=subgraph_name)

    for subgraph in g.get_subgraphs():
        sg_name = (
            subgraph.get_name()
            if len(subgraph_name) == 0
            else ".".join([subgraph_name, subgraph.get_name()])
        )
        collect(subgraph, node_id_to_nodes, subgraph_name=sg_name)

    return node_id_to_nodes


def to_polkadot_nodes(dotfile_path: DotFile) -> List[PolkadotNode]:
    gs = pydot.graph_from_dot_file(dotfile_path)
    assert len(gs) == 1
    g = gs[0]
    node_id_to_nodes = dict()
    collect(g, node_id_to_nodes)
    return list(node_id_to_nodes.values())


if __name__ == "__main__":
    import sys
    _ = to_polkadot_nodes(sys.path[1])
