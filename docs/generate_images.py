from pathlib import Path

import erdantic as erd
from erdantic.core import EntityRelationshipDiagram
import erdantic.examples.pydantic as pydantic_examples

ASSETS_DIR = Path(__file__).resolve().parent / "docs" / "assets"


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


if __name__ == "__main__":
    generate_example_diagram()
    generate_erdantic_diagram()
