from setuptools import setup, find_packages
from pathlib import Path


def load_requirements(path: Path):
    requirements = []
    with path.open("r") as fp:
        for line in fp.readlines():
            if line.startswith("-r"):
                requirements += load_requirements(line.split(" ")[1].strip())
            else:
                requirement = line.strip()
                if requirement and not requirement.startswith("#"):
                    requirements.append(requirement)
    return requirements


readme = Path("README.md").read_text(encoding="UTF-8")

requirements = load_requirements(Path(__file__).parent / "requirements.txt")

setup(
    author="Jay Qi",
    author_email="jayqi.opensource@gmail.com",
    python_requires=">=3.6",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description=("Draw entity relation diagrams for Pydantic models using GraphViz."),
    install_requires=requirements,
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    name="pydantic_erd",
    packages=find_packages(),
    project_urls={},
    url="",
    version="0.1.0",
)
