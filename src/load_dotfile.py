from dataclasses import dataclass
from typing import Dict, List, Optional

import pydot

DOT_RESERVED_NODE_IDS = frozenset({"graph", "node", "edge", ""})
CHARS_TO_STRIP = "\\\r\n\t '\""
NodeId = str
URL = str
Expected = str


@dataclass()
class PolkadotNode:
    node_id: NodeId
    url: Optional[URL] = None
    expected: Optional[Expected] = None


DotFile = str


def _collect(
    g: pydot.Graph, node_id_to_nodes: Dict[NodeId, PolkadotNode]
) -> Dict[NodeId, PolkadotNode]:

    for node in g.get_nodes():
        node_id = node.get_name().strip(CHARS_TO_STRIP)
        if node_id in DOT_RESERVED_NODE_IDS:
            continue
        attrs = {k.lower(): v for k, v in node.get_attributes().items()}
        url = attrs.get("url", None)
        if url is not None:
            url = url.strip(CHARS_TO_STRIP)

        expected = attrs.get("expected", None)
        if expected is not None:
            expected = expected.strip()

        pdn = PolkadotNode(node_id, url, expected)
        node_id_to_nodes[node_id] = pdn

    for edge in g.get_edges():
        src = edge.get_source()
        dst = edge.get_destination()
        if src not in node_id_to_nodes:
            node_id_to_nodes[src] = PolkadotNode(src)
        if dst not in node_id_to_nodes:
            node_id_to_nodes[dst] = PolkadotNode(dst)

    for subgraph in g.get_subgraphs():
        _collect(subgraph, node_id_to_nodes)

    return node_id_to_nodes


def to_polkadot_nodes(dotfile_path: DotFile) -> List[PolkadotNode]:
    gs = pydot.graph_from_dot_file(dotfile_path)
    assert len(gs) == 1
    g = gs[0]
    node_id_to_nodes = dict()
    _collect(g, node_id_to_nodes)
    return list(node_id_to_nodes.values())
