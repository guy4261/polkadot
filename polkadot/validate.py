#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import re
from enum import Enum
from typing import List, Tuple
from urllib.parse import urlparse

import git
import requests

from polkadot.config import PolkadotConfig, RepoConfig, load_polkadot_config
from polkadot.load_dotfile import CHARS_TO_STRIP, PolkadotNode, to_polkadot_nodes

CONTENT_PATTERN = r"(([\w]+)[\s\t]+(\[.*?\]))"
C_CONTENT_PATTERN = re.compile(CONTENT_PATTERN, re.DOTALL)
URL_PATTERN = r'URL[\s]?=[\s]?"(.*?)"'
C_URL_PATTERN = re.compile(URL_PATTERN)
EXPECTED_PATTERN = r'expected[\s\t]*=[\s\t]*"(.*?)"'
C_EXPECTED_PATTERN = re.compile(EXPECTED_PATTERN)
DOT_RESERVED_NODE_IDS = frozenset({"node", "edge", "graph"})
URL = str
Expected = str
RawURL = str
RawContent = bytes
ErrorMessage = str
LineNo = int

EXAMPLE = os.path.realpath(
    os.path.join(os.path.dirname(__file__),
                 "../examples/good_bad_ugly/diagram.dot")
)
EXAMPLE = f", example: {EXAMPLE}" if os.path.isfile(EXAMPLE) else ""


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=str,
                        help=f"dot/gv file to validate{EXAMPLE}")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser


class ResultType(Enum):

    found = "✅"
    missing = "❌"
    elsewhere = "🚧"
    url_only = "🔗"
    expected_only = "👀"
    empty = "👻"
    failed = "🎃"


SHA1 = str
LocalPath = str
LineNo1 = int
LineNo0 = int


def break_git_link(git_link: str) -> Tuple[SHA1, LocalPath, LineNo1]:
    """
    https://github.com/guy4261/polkadot/blob/4ac8dec74950fd7107c8c9d3308d890d4695471f/src/validate.py#L125
    https://gitlab.com/guy4261/polkadot/blob/4ac8dec74950fd7107c8c9d3308d890d4695471f/src/validate.py#L125
    """

    parsed = urlparse(git_link)
    user, project, blob, sha, path = parsed.path.strip(os.path.sep).split(
        os.path.sep, 4
    )  # blob/sha/path
    lineno1 = int(parsed.fragment.strip("L"))
    return sha, path, lineno1


def validate_node(node: PolkadotNode, config: PolkadotConfig) -> ResultType:

    url = node.url
    expected = node.expected

    if url is None and expected is None:
        return ResultType.empty

    if url is not None and expected is None:
        return ResultType.url_only

    if url is None and expected is not None:
        return ResultType.expected_only

    hit = False
    repo_config: RepoConfig
    for repo_config in config.repos:
        starts = ("https://" + repo_config.remote, repo_config.remote)
        if url.startswith(starts):
            hit = True
            break

    if not hit:
        return ResultType.failed

    # now we know we've been hit
    sha1, localpath, lineno1 = break_git_link(url)
    lineno0 = lineno1 - 1

    repo = git.Repo(repo_config.local)
    repo.commit(sha1)
    # print(commit.committed_datetime.strftime("%Y/%m/%d %H:%M:%S"))

    origin = repo.remote().name
    content = repo.git.show(
        f"{origin}/{repo_config.default_branch}:{localpath}")
    lines = [l.strip(CHARS_TO_STRIP) for l in content.splitlines()]

    try:
        actual = lines[lineno0].strip(CHARS_TO_STRIP)
    except IndexError:
        actual = None
    if actual == expected:
        return ResultType.found
    try:
        lines.index(expected)
        return ResultType.elsewhere
    except ValueError:
        # print(expected)
        # print(actual)
        return ResultType.missing


"""
local: bool = False,
verbose: bool = False,
repos_config: Optional[Dict[str, str]] = None,
"""


def validate(
    nodes: List[PolkadotNode],
    polkadot_config: PolkadotConfig,
) -> bool:

    nodes.sort(key=lambda node: node.subgraph)
    results = []
    for node in nodes:
        try:
            result = validate_node(node, polkadot_config)
            results.append(result)
        except Exception as e:
            result = ResultType.failed
            results.append(result)
            print(str(e))
        print(f"{result.value}  {node.node_id}")

    return (
        len(
            set(results) & {ResultType.failed,
                            ResultType.missing, ResultType.elsewhere}
        )
        == 0
        and ResultType.found in results
    )


def main():
    parser = get_parser()
    args = parser.parse_args()
    dotfile_path = args.target
    ns = to_polkadot_nodes(dotfile_path)
    repos_config = load_polkadot_config()

    is_valid = validate(ns, repos_config)

    if args.verbose:
        """
        # If I'd ever want it
        try:
            from blessed import Terminal
            term = Terminal()
            legend_title = term.underline("Legend")
        except ModuleNotFoundError:
        """

        print()
        legend_title = "Legend\n──────"
        print(legend_title)
        for e in ResultType:
            print(f"{e.value} {e.name.capitalize()}")

    if is_valid:
        print(f"{dotfile_path} is OK!")
        exit(0)
    else:
        print(f"{dotfile_path} is stale")
        exit(1)


if __name__ == "__main__":
    main()
