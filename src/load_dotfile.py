from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pydot

DOT_RESERVED_NODE_IDS = frozenset({"graph", "node", "edge", ""})


@dataclass()
class PolkadotNode:
    node_id: str
    url: Optional[str] = None
    expected: Optional[str] = None


NodeId = str


def collect(
    g: pydot.Graph, node_id_to_nodes: Optional[Dict[NodeId, PolkadotNode]] = None
) -> Union[List[PolkadotNode], Dict[NodeId, PolkadotNode]]:

    init = node_id_to_nodes is None
    if init:
        node_id_to_nodes = dict()

    for node in g.get_nodes():
        node_id = node.get_name().strip("\\\r\n\t '\"")
        if node_id in DOT_RESERVED_NODE_IDS:
            continue
        attrs = {k.lower(): v for k, v in node.get_attributes().items()}
        url = attrs.get("url", None)
        if url is not None:
            url = url.strip("\\\r\n\t '\"")

        expected = attrs.get("expected", None)
        if expected is not None:
            expected = expected.strip("\\\r\n\t '\"")

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
        collect(subgraph, node_id_to_nodes)

    if init:
        return list(node_id_to_nodes.values())

    return node_id_to_nodes


if __name__ == "__main__":
    path = "/Users/guyr/ziprecruiter/company/store/sections/design.gv"
    gs = pydot.graph_from_dot_file(path)
    assert len(gs) == 1
    g = gs[0]
    ns = collect(g)
