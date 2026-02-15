from pathlib import Path
import sys

from tests.snapshot_cases import SNAPSHOT_CASES

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


def generate_example_assets(name: str, model_or_module: object, out_dir: Path):
    """Generate all static assets for user-facing example cases."""
    out_dir.mkdir(parents=True, exist_ok=True)
    diagram = erd.create(model_or_module)

    diagram.draw(out=out_dir / f"{name}.png")
    diagram.draw(out=out_dir / f"{name}.svg")
    with (out_dir / f"{name}.dot").open("w") as fp:
        fp.write(diagram.to_dot())
    with (out_dir / f"{name}.json").open("w") as fp:
        fp.write(diagram.model_dump_json(indent=2))
    with (out_dir / f"{name}.d2").open("w") as fp:
        fp.write(diagram.to_d2())


def generate_snapshot_assets(name: str, model_or_module: object, out_dir: Path):
    """Generate only text-based renderer snapshots for test-focused cases."""
    out_dir.mkdir(parents=True, exist_ok=True)
    diagram = erd.create(model_or_module)

    with (out_dir / f"{name}.dot").open("w") as fp:
        fp.write(diagram.to_dot())
    with (out_dir / f"{name}.d2").open("w") as fp:
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
        plugin = module.__name__.rsplit(".", 1)[1]
        generate_example_assets(plugin, module.Party, out_dir)

    snapshots_dir = out_dir / "snapshots"
    for case_name, model in SNAPSHOT_CASES:
        generate_snapshot_assets(case_name, model, snapshots_dir)
