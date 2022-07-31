import pygraphviz as pgv


def assert_dot_equals(left: str, right: str):
    """Assert two DOT language representations specify identical graphs."""
    gleft = pgv.AGraph(left)
    gright = pgv.AGraph(right)
    assert gleft == gright
