import inspect
import logging
from pathlib import Path
import textwrap

from typer.testing import CliRunner

from erdantic.cli import app
import erdantic.plugins

logger = logging.getLogger("mkdocs")
runner = CliRunner(mix_stderr=False)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _read_readme():
    readme_path = REPO_ROOT / "README.md"
    logger.info("Reading README from %s", readme_path)
    readme_text = readme_path.read_text()
    readme_text = readme_text.replace(
        "./docs/docs/assets/example_diagram.svg",
        "assets/example_diagram.svg",
    )
    readme_text = readme_text.replace(
        "./HISTORY.md",
        "changelog.md",
    )
    return readme_text


def _read_changelog():
    changelog_path = REPO_ROOT / "HISTORY.md"
    logger.info("Reading CHANGELOG from %s", changelog_path)
    changelog_text = changelog_path.read_text()
    return changelog_text


def on_page_read_source(page, **kwargs):
    if page.title == "Home":
        return _read_readme()
    if page.title == "Changelog":
        return _read_changelog()
    return None


def _inject_cli_help(markdown: str):
    logger.info("Injecting CLI --help output into page markdown")
    result = runner.invoke(app, ["--help"], prog_name="erdantic", env={"TERM": "dumb"})
    help_text = result.stdout
    return markdown.replace("{{INJECT CLI HELP}}", help_text)


def _inject_model_predicate_source(markdown: str):
    logger.info("Injecting ModelPredicate source code into page markdown")
    source = inspect.getsource(erdantic.plugins.ModelPredicate)
    code_block = textwrap.dedent("""\
    ```python
    {source}
    ```
    """)
    code_block = code_block.format(source=source)
    code_block = textwrap.indent(code_block, "    ")
    return markdown.replace("{{INJECT MODELPREDICATE SOURCE}}", code_block)


def _inject_model_field_extractor_source(markdown: str):
    logger.info("Injecting ModelFieldExtractor source code into page markdown")
    source = inspect.getsource(erdantic.plugins.ModelFieldExtractor)
    code_block = textwrap.dedent("""\
    ```python
    {source}
    ```
    """)
    code_block = code_block.format(source=source)
    code_block = textwrap.indent(code_block, "    ")
    return markdown.replace("{{INJECT MODELFIELDEXTRACTOR SOURCE}}", code_block)


def _inject_pydantic_with_default_column_example(markdown: str):
    logger.info("Injecting pydantic_with_default_column.py source code into page markdown")
    code_block = (REPO_ROOT / "tests" / "pydantic_with_default_column.py").read_text()
    return markdown.replace("{{INJECT PYDANTIC_WITH_DEFAULT_COLUMN SOURCE}}", code_block)


def on_page_markdown(markdown, page, **kwargs):
    if page.title == "CLI Help":
        return _inject_cli_help(markdown)
    if page.title == "Extending or Modifying":
        markdown = _inject_model_predicate_source(markdown)
        markdown = _inject_model_field_extractor_source(markdown)
        markdown = _inject_pydantic_with_default_column_example(markdown)
        return markdown
    return None
