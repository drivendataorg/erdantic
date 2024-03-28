from pathlib import Path
from types import ModuleType

import erdantic as erd
import erdantic._version
import erdantic.examples

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"

# monkeypatch __version__ and watermark
_default_graph_attrs = dict(erdantic.core.DEFAULT_GRAPH_ATTR)
_default_graph_attrs["label"] = _default_graph_attrs["label"].replace(
    f"v{erd.__version__}", "vTEST"
)
erdantic.core.DEFAULT_GRAPH_ATTR = tuple(_default_graph_attrs.items())
erd.__version__ = erdantic.core.__version__ = erdantic._version.__version__ = "TEST"


def create_assets(examples: ModuleType):
    plugin = examples.__name__.rsplit(".", 1)[1]
    (ASSETS_DIR).mkdir(exist_ok=True)
    diagram = erd.create(examples.Party)

    diagram.draw(out=ASSETS_DIR / f"{plugin}.png")
    diagram.draw(out=ASSETS_DIR / f"{plugin}.svg")
    with (ASSETS_DIR / f"{plugin}.dot").open("w") as fp:
        fp.write(diagram.to_dot())
    with (ASSETS_DIR / f"{plugin}.json").open("w") as fp:
        fp.write(diagram.model_dump_json(indent=2))


if __name__ == "__main__":
    for module in [
        erdantic.examples.attrs,
        erdantic.examples.dataclasses,
        erdantic.examples.pydantic,
        erdantic.examples.pydantic_v1,
    ]:
        create_assets(module)
