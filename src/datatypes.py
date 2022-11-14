from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional

DEFAULT_BRANCH_NAME: str = "main"


@dataclass
class PathSpec:
	path: str
	line_start: int
	line_end: Optional[int]


class Node(object):

	ATTR_URL = "URL"
	ATTR_PATHSPEC = "pathspec"
	ATTR_EXPECTED = "expected"

	def __init__(node_id: str, **attrs: Dict[str, Any]):
		self.node_id = node_id
		self.__attributes = attrs

	def get_url(self) -> Optional[str]:
		return self.__attributes.get(ATTR_URL)

	def get_pathspec(self) -> Optional[PathSpec]:
		return self.__attributes.get(ATTR_PATHSPEC)

	def get_expected(self) -> Optional[str]:
		return self.__attributes.get(ATTR_EXPECTED)

	def set_url(self, url: str):
		self.__attributes[ATTR_URL] = url

	def get_pathspec(self, pathspec: PathSpec) -> Optional[str]:
		self.__attributes[ATTR_PATHSPEC] = pathspec

	def get_expected(self, expected: str) -> Optional[str]:
		self.__attributes[ATTR_EXPECTED] = expected
	

@dataclass
class ProjectInfo:
	alias: str
	repo_url: str
	default_branch: str = DEFAULT_BRANCH_NAME


@dataclass
class LocalConfig:
	alias_root: Dict[str, Path]


class PathspecType(Enum):

	# https://github.com/rochacbruno/python-project-template/blob/main/setup.py#L2-L4
	GitHub = auto()

	# https://gitlab.com/gitlab-org/gitlab/-/blob/master/.gitignore#L5-23
	GitLab = auto()

	# foo.py:19
	JetBrains = SublimeText = auto()

	# https://stackoverflow.com/a/36211296  # [nano|vi] +10 file.txt
	nano = vi = auto()


class ValidationStatus(Enum):

	Match = auto()
	MatchedElseWhere = auto()
	Unmatched = auto()
	ExpectedNotSupplied = auto()
