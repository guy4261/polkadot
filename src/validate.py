#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import re
from typing import Dict
from typing import Optional
from typing import Tuple
from urllib.parse import urlparse

import requests

CONTENT_PATTERN = "(([\w]+) (\[.*?\]))"
C_CONTENT_PATTERN = re.compile(CONTENT_PATTERN, re.DOTALL)
URL_PATTERN = r'URL[\s]?=[\s]?"(.*?)"'
C_URL_PATTERN = re.compile(URL_PATTERN)
EXPECTED_PATTERN = r'expected[\s]?=[\s]?"(.*?)"'
C_EXPECTED_PATTERN = re.compile(EXPECTED_PATTERN)

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
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    return parser


def get_url_and_expected(node_details: str) -> Tuple[Optional[URL], Optional[Expected]]:
    url = C_URL_PATTERN.findall(node_details)
    if len(url) == 1:
        url = url[0]
    else:
        url = None

    expected = C_EXPECTED_PATTERN.findall(node_details)
    if len(expected) == 1:
        expected = expected[0]
    else:
        expected = None

    return url, expected


def get_actual_github_url(url: str) -> Tuple[Optional[RawURL], Optional[ErrorMessage]]:
    try:
        parsed = urlparse(url)
        user, repo, blob, branch, path = parsed.path.strip("/").split("/", 4)
        return f"{parsed.scheme}://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}", None
    except Exception as e:
        return None, str(e)


def get_lineno(url: str) -> Tuple[Optional[LineNo], Optional[ErrorMessage]]:
    try:
        parsed = urlparse(url)
        return int(parsed.fragment.strip("L")), None
    except Exception as e:
        return None, str(e)


def get_github_raw_content(raw_url: RawURL) -> Tuple[Optional[RawContent], Optional[ErrorMessage]]:
    try:
        resp = requests.get(raw_url)
        return resp.content, None
    except Exception as e:
        return None, str(e)


def validate(dotfile_path: str, local: bool = False, verbose: bool = False, repos_config: Optional[Dict[str, str]] = None) -> bool:

    content = open(dotfile_path).read()
    findings = C_CONTENT_PATTERN.findall(content)

    node_ids_to_tuple_url_expected = {}

    for full, node_id, node_details in findings:
        url, expected = get_url_and_expected(node_details)
        if url is not None and expected is not None:
            node_ids_to_tuple_url_expected[node_id] = (url, expected.strip("\r\n\t "))

    warnings = 0
    errors = 0
    print()
    for node_id, (url, expected) in node_ids_to_tuple_url_expected.items():
        if local:
            local_path = url
            for k, v in repos_config.items():
                local_path = local_path.replace(k, v)
            local_path = os.path.expanduser(os.path.expandvars(local_path))
            local_path, lineno1 = local_path.rsplit("#L", 1)
            lines = [line.strip("\r\n\t ") for line in open(local_path).readlines()]
        else:
            raw_url, err = get_actual_github_url(url)
            raw_content, err = get_github_raw_content(raw_url)
            lines = [line.strip("\r\n\t ") for line in raw_content.decode("utf-8").splitlines()]


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
                suffix = f" expected {repr(expected)} was instead found on line {lines.index(expected) + 1}." if verbose else ""
            else:
                errors += 1
                icon = "❌"
                suffix = f" expected {repr(expected)} but found {repr(actual)}." if verbose else ""

        print(f"{icon} {node_id}{suffix}")

    print()
    if warnings == 0 and errors == 0:
        print(f"{dotfile_path} is OK!")
        return True
    else:
        print(f"{dotfile_path} is stale: found {warnings} warnings and {errors} errors.")
        return False


def main():
    parser = get_parser()
    args = parser.parse_args()

    is_valid = validate(
        args.target,
        local=args.local,
        verbose=args.verbose,
        repos_config={"https://github.com/guy4261/polkadot/blob/main": os.path.dirname(os.path.dirname(__file__))},
    )

    if is_valid:
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()
