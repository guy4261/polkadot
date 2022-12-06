from typing import List

import pydot

from polkadot.config import load_polkadot_config
from polkadot.load_dotfile import PolkadotNode, collect
from polkadot.validate import validate

try:
    import pptx
except ModuleNotFoundError:
    print("python-pptx is missing: Please run '$ pip install python-pptx'")
    exit(1)


def _pptx_to_pydot_graphs(path: str) -> List[pydot.Graph]:
    def _get_shape_text(shape: pptx.shapes.base.BaseShape):
        if hasattr(shape, "shapes"):
            return "".join(map(_get_shape_text, shape.shapes))
        else:
            return shape.text

    rv: List[pydot.Graph] = []
    pres = pptx.Presentation(path)
    for slide in pres.slides:
        dot_data = "digraph G{"
        for shape in slide.shapes:
            dot_data += _get_shape_text(shape) + "\n"
        dot_data += "\n}"
        graph = pydot.graph_from_dot_data(dot_data)[0]
        rv.append(graph)

    return rv


def pptx_to_polkadot_nodes(path: str) -> List[PolkadotNode]:
    graphs = _pptx_to_pydot_graphs(path)
    assert len(graphs) == 1
    g = graphs[0]
    node_id_to_nodes = dict()
    collect(g, node_id_to_nodes)
    rv = list(node_id_to_nodes.values())
    rv.sort(key=lambda node: node.node_id)
    return rv


validate(pptx_to_polkadot_nodes("example.pptx"), load_polkadot_config())
