#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import re
from enum import Enum
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import git
import requests

from config import PolkadotConfig, RepoConfig, load_polkadot_config
from load_dotfile import CHARS_TO_STRIP, PolkadotNode, to_polkadot_nodes

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
    os.path.join(os.path.dirname(__file__), "../examples/good_bad_ugly/diagram.dot")
)
EXAMPLE = f", example: {EXAMPLE}" if os.path.isfile(EXAMPLE) else ""


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=str, help=f"dot/gv file to validate{EXAMPLE}")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser


def get_url_and_expected(node_details: str) -> Tuple[Optional[URL], Optional[Expected]]:

    expected = C_EXPECTED_PATTERN.findall(node_details)
    if len(expected) == 1:
        expected = expected[0]
    else:
        expected = None

    url = C_URL_PATTERN.findall(node_details)
    if len(url) == 1:
        url = url[0]
    else:
        url = None

    return url, expected


def get_actual_github_url(url: str) -> Tuple[Optional[RawURL], Optional[ErrorMessage]]:
    try:
        parsed = urlparse(url)
        user, repo, blob, branch, path = parsed.path.strip("/").split("/", 4)
        return (
            f"{parsed.scheme}://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}",
            None,
        )
    except Exception as e:
        return None, str(e)


def get_lineno(url: str) -> Tuple[Optional[LineNo], Optional[ErrorMessage]]:
    try:
        parsed = urlparse(url)
        return int(parsed.fragment.strip("L")), None
    except Exception as e:
        return None, str(e)


def get_github_raw_content(
    raw_url: RawURL,
) -> Tuple[Optional[RawContent], Optional[ErrorMessage]]:
    try:
        resp = requests.get(raw_url)
        return resp.content, None
    except Exception as e:
        return None, str(e)


def load_nodes_using_regex(dotfile_path: str):
    content = open(dotfile_path).read()
    findings = C_CONTENT_PATTERN.findall(content)

    node_ids_to_tuple_url_expected = {}

    for full, node_id, node_details in findings:
        if node_id in DOT_RESERVED_NODE_IDS:
            continue
        url, expected = get_url_and_expected(node_details)
        if url is not None:
            url = url.strip("\r\n\t ")
        if expected is not None:
            expected = expected.strip("\r\n\t ")
        node_ids_to_tuple_url_expected[node_id] = (url, expected)

    return node_ids_to_tuple_url_expected


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
    user, project, blob, sha, path = parsed.path.split(os.path.sep, 4)  # blob/sha/path
    path, lineno1 = path.rsplit("#")
    lineno1 = int(lineno1.strip("L"))
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
        if url.startswith(repo_config.remote):
            hit = True
            break

    if not hit:
        return ResultType.failed

    # now we know we've been hit
    sha1, localpath, lineno1 = break_git_link(url)
    local_path = os.path.join(repo_config.local, localpath)
    lineno0 = lineno1 - 1

    repo = git.Repo(local_path)
    commit = repo.commit(sha1)
    print(commit.committed_datetime.strftime("%Y/%m/%d %H:%M:%S"))

    origin = repo.remote().name
    content = repo.git.show(f"{origin}/{repo_config.default_branch}:{localpath}")
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

    results = []
    for node in nodes:
        try:
            result = validate_node(node, polkadot_config)
            results.append(result)
        except:
            result = ResultType.failed
            results.append(result)
        print(f"{result.value}  {node.node_id}")

    return (
        len(
            set(results) & {ResultType.failed, ResultType.missing, ResultType.elsewhere}
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

"""

    warnings = 0
    errors = 0
    print()
    print(f"Found {len(nodes)} nodes")
    for node in nodes:
        node_id = node.node_id
        url = node.url
        expected = node.expected
        if expected is None:
            if url is None:
                icon = "👻"
                suffix = " has no 'URL', 'expected' attributes." if verbose else ""
            else:
                icon = "🔗"
                suffix = f" only has 'URL' attribute: {url}" if verbose else ""
            print(f"{icon} {node_id}{suffix}")
            continue

        if local:
            local_path = url
            for k, v in repos_config.items():
                local_path = local_path.replace(k, v)
            if local_path == url:
                print("Failed resolving URL:", url)
                continue
            local_path, lineno1 = local_path.rsplit("#L", 1)
            local_path = os.path.expanduser(local_path)

            if not os.path.isfile(local_path):
                print(f"Path not found: {local_path}")
                continue
            lines = [line.strip("\\\r\n\t '\"") for line in open(local_path).readlines()]
        else:
            raw_url, err = get_actual_github_url(url)
            raw_content, err = get_github_raw_content(raw_url)
            if err is not None:
                print(err)
                continue
            else:
                lines = [line.strip("\\\r\n\t '\"") for line in raw_content.decode("utf-8").splitlines()]

        lineno1, err = get_lineno(url)
        lineno1 = int(lineno1)
        lineno0 = lineno1 - 1

        actual = lines[lineno0].strip()

        if expected == actual:
            icon = "✅"
            suffix = f" found {repr(actual)}." if verbose else ""
        else:
            if expected in lines:
                warnings += 1
                icon = "🚧"
                suffix = (
                    f" expected {repr(expected)} was instead found on line {lines.index(expected) + 1}."
                    if verbose
                    else ""
                )
            else:
                errors += 1
                icon = "❌"
                suffix = f" expected {repr(expected)} but found {repr(actual)}." if verbose else ""

        print(f"{icon} {node_id}{suffix}")

    print()
    if warnings == 0 and errors == 0:
        return True
    else:
        print(f"Found {warnings} warnings and {errors} errors.")
        return False
"""
