from pathlib import Path
from types import ModuleType

import erdantic as erd
import erdantic.erd
import erdantic.examples.dataclasses
import erdantic.examples.pydantic
import erdantic._version

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"

# monkeypatch __version__
erd.__version__ = erdantic.erd.__version__ = erdantic._version.__version__ = "TEST"


def create_assets(examples: ModuleType):
    stem = examples.__name__.rsplit(".", 1)[1]
    (ASSETS_DIR / stem).mkdir(exist_ok=True)
    diagram = erd.create(examples.Party)

    diagram.draw(out=ASSETS_DIR / stem / "diagram.png")
    diagram.draw(out=ASSETS_DIR / stem / "diagram.svg")
    with (ASSETS_DIR / stem / "diagram.dot").open("w") as fp:
        fp.write(diagram.to_dot())


if __name__ == "__main__":
    for module in [erdantic.examples.dataclasses, erdantic.examples.pydantic]:
        create_assets(module)
