#!/usr/bin/env python
from typing import Optional
from typing import Tuple
from enum import Enum
from enum import auto


class GvNode(object):

	def __init__(self, path: str, lineno0: int, expected: str, url: Optional[str] = None):
		"""

		url: URL for the line.
		path: path to file on local directory.
		lineno0: 0-based line number.
		expected: expected line in the given pathspec.
		"""
		self.path = path
		self.lineno0 = lineno0
		self.expected = expected.strip()
		self.url = url

	def readlines(self) -> str:
		return [_.strip() for _ in open(self.path).readlines()]

	def validate(self) -> bool:
		"""Validate expected string is actually in self.path:self.lineno."""
		
		actual = self.readlines()[self.lineno0]
		assert self.expected == actual, (self.expected, actual, self.lineno0)

	def check(self):
		lines = self.readlines()
		actual = lines[self.lineno0]
		if actual == self.expected:
			print(f"✅  {self.expected}")
		else:
			options = [i for i, _ in enumerate(lines) if _ == self.expected]
			if len(options) == 0:
				print(f"❌  {self.actual}")
			else:
				for option in options:
					print(f"⚠️  {option + 1} {self.expected}")


	@staticmethod
	def pathspec1_to_path_lineno0(pathspec1: str) -> Tuple[str, int]:
		"""

		pathspec1: path:lineno to expected, with the line number being 1-based (like it would display in an IDE).
		"""
		path, lineno1 = pathspec1.rsplit(":", 1)
		lineno0 = int(lineno1) - 1
		return path, lineno0
