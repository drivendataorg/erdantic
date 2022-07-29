import re

import pygraphviz as pgv


def assert_dot_equals(left: str, right: str):
    """Assert two DOT language representations specify identical graphs."""
    gleft = pgv.AGraph(left)
    gright = pgv.AGraph(right)
    assert gleft == gright


# https://stackoverflow.com/a/14693789
ANSI_ESCAPE_REGEX = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_ansi_escape_codes(input: str) -> str:
    return ANSI_ESCAPE_REGEX.sub("", input)
