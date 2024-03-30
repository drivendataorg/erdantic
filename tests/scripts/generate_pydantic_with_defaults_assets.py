from pathlib import Path

import tests.pydantic_with_default_column

import erdantic as erd
import erdantic._version
import erdantic.examples.pydantic

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"

# monkeypatch __version__ and watermark
_default_graph_attrs = dict(erdantic.core.DEFAULT_GRAPH_ATTR)
_default_graph_attrs["label"] = _default_graph_attrs["label"].replace(
    f"v{erd.__version__}", "vTEST"
)
erdantic.core.DEFAULT_GRAPH_ATTR = tuple(_default_graph_attrs.items())
erd.__version__ = erdantic.core.__version__ = erdantic._version.__version__ = "TEST"


if __name__ == "__main__":
    filename = "pydantic_with_default_column"
    out_dir = ASSETS_DIR / "test_core-test_subclass"
    (out_dir).mkdir(exist_ok=True)
    diagram = tests.pydantic_with_default_column.EntityRelationshipDiagramWithDefault()
    diagram.add_model(erdantic.examples.pydantic.Party)

    diagram.draw(out=out_dir / f"{filename}.png")
    diagram.draw(out=out_dir / f"{filename}.svg")
    with (out_dir / f"{filename}.dot").open("w") as fp:
        fp.write(diagram.to_dot())
    with (out_dir / f"{filename}.json").open("w") as fp:
        fp.write(diagram.model_dump_json(indent=2))
