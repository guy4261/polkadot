#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import os
import re
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from urllib.parse import urlparse

import pydot
import requests

from load_dotfile import PolkadotNode
from load_dotfile import collect

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

EXAMPLE_DOTFILE = os.path.realpath(os.path.join(os.path.dirname(__file__), "../examples/good_bad_ugly/diagram.dot"))


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=str, help=f"dot/gv file to validate, example: {EXAMPLE_DOTFILE}")
    parser.add_argument("-l", "--local", action="store_true")
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


def validate(
    nodes: List[PolkadotNode],
    local: bool = False,
    verbose: bool = False,
    repos_config: Optional[Dict[str, str]] = None,
) -> bool:

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
                suffix = f" has no 'expected' attribute: {url}" if verbose else ""
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


def main():
    parser = get_parser()
    args = parser.parse_args()
    dotfile_path = args.target

    gs = pydot.graph_from_dot_file(dotfile_path)
    assert len(gs) == 1
    g = gs[0]
    ns = collect(g)

    """
    ns = [
        PolkadotNode(node_id='classify_section_title',
                     url='https://git.zr.org/ziprecruiter/ziprecruiter/-/blob/main/company/company_section/extract_company_data.py#L28',
                     expected='"def get_company_sections(raw_description: str, org_synonyms: List[List[str]], only_english: bool = True,"')
    ]
    print("\n".join(map(str, ns)))
    """

    repos_config = json.load(open(os.path.expanduser("~/.polkadot.json")))
    repos_config = {record["remote"]: record["local"] for record in repos_config["repos"]}

    is_valid = validate(
        ns,
        local=args.local,
        verbose=args.verbose,
        repos_config=repos_config,
    )

    if is_valid:
        print(f"{dotfile_path} is OK!")
        exit(0)
    else:
        print(f"{dotfile_path} is stale")
        exit(1)


if __name__ == "__main__":
    main()
