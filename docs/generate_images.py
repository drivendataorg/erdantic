from pathlib import Path
import subprocess

import pygraphviz as pgv

import erdantic as erd
from erdantic.core import Cardinality, EntityRelationshipDiagram, Modality
import erdantic.examples.pydantic as pydantic_examples

ASSETS_DIR = Path(__file__).resolve().parent / "docs" / "assets"
REPO_ROOT = ASSETS_DIR.parents[2]


def generate_example_diagram():
    """Generate an ERD diagram for pydantic examples."""
    diagram = erd.create(pydantic_examples)
    diagram.draw(ASSETS_DIR / "example_diagram.png")
    diagram.draw(ASSETS_DIR / "example_diagram.svg")


def generate_erdantic_diagram():
    """Generate an ERD diagram for erdantic itself."""
    diagram = erd.create(EntityRelationshipDiagram)
    graph_attr = {"ranksep": 0.8}
    diagram.draw(ASSETS_DIR / "erdantic_diagram.svg", graph_attr=graph_attr)
    diagram.draw(ASSETS_DIR / "erdantic_diagram.png", graph_attr=graph_attr)


def generate_edges():
    for cardinality, modality in [
        (Cardinality.ONE, Modality.ONE),
        (Cardinality.ONE, Modality.ZERO),
        (Cardinality.MANY, Modality.UNSPECIFIED),
        (Cardinality.MANY, Modality.ZERO),
    ]:
        graph = pgv.AGraph(directed=True, rankdir="LR", pad=0.005)
        graph.node_attr["fontsize"] = 11.0
        graph.node_attr["margin"] = "0.11,0.015"
        graph.add_node("source", shape="plaintext")
        graph.add_node("target", shape="plaintext")
        graph.add_edge("source", "target", arrowhead=cardinality.to_dot() + modality.to_dot())
        graph.draw(ASSETS_DIR / f"edge-{cardinality.value}-{modality.value}.png", prog="dot")


def copy_pydantic_with_default_diagram():
    subprocess.run(
        ["python", f"{Path(__file__).parent}/generate_pydantic_with_default_column_diagram.py"]
    )


if __name__ == "__main__":
    generate_example_diagram()
    generate_erdantic_diagram()
    generate_edges()
    copy_pydantic_with_default_diagram()
