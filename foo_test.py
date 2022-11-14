#!/usr/bin/env python
from foo import GvNode
from random import randint


path = "foo.py"
lines = [_.strip() for _ in open("foo.py").readlines()]

for lineno0, line in enumerate(lines):
	lspec = f"{path}:{lineno0 + 1}"
	path, lineno0 = GvNode.pathspec1_to_path_lineno0(lspec)
	node = GvNode(path, lineno0, line)
	node.validate()
	node.check()

	rand = lineno0
	while rand == lineno0:
		rand = randint(0, len(lines) - 1)
	node = GvNode(path, rand, line)
	try:
		node.validate()
		assert False
	except AssertionError:
		assert True
	node.check()