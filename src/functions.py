from datatypes import Node
from typing import Dict
from typing import List


import pydot


def get_nodes(filename: str) -> Dict[str, Node]:
	g: List[pydot.Dot] = pydot.graph_from_dot_file("./design.gv")
	assert isinstance(g, list)
	assert len(g) == 1
	g: pydot.Dot = g[0]
