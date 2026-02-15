from pathlib import Path
import sys
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


def create_assets(examples: ModuleType, out_dir: Path):
    plugin = examples.__name__.rsplit(".", 1)[1]
    diagram = erd.create(examples.Party)

    diagram.draw(out=out_dir / f"{plugin}.png")
    diagram.draw(out=out_dir / f"{plugin}.svg")
    with (out_dir / f"{plugin}.dot").open("w") as fp:
        fp.write(diagram.to_dot())
    with (out_dir / f"{plugin}.json").open("w") as fp:
        fp.write(diagram.model_dump_json(indent=2))
    with (out_dir / f"{plugin}.d2").open("w") as fp:
        fp.write(diagram.to_d2())


if __name__ == "__main__":
    out_dir = ASSETS_DIR / sys.argv[1]
    out_dir.mkdir(exist_ok=True)
    modules = [
        erdantic.examples.attrs,
        erdantic.examples.dataclasses,
        erdantic.examples.pydantic,
    ]
    if sys.version_info < (3, 14):
        modules.append(erdantic.examples.pydantic_v1)
    for module in modules:
        create_assets(module, out_dir)
