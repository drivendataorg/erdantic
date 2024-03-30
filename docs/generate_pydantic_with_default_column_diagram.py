from pathlib import Path

from tests.pydantic_with_default_column import EntityRelationshipDiagramWithDefault

from erdantic.examples.pydantic import Party

ASSETS_DIR = Path(__file__).resolve().parent / "docs" / "assets"

diagram = EntityRelationshipDiagramWithDefault()
diagram.add_model(Party)
diagram.draw(ASSETS_DIR / "pydantic_with_default_column_diagram.png")
