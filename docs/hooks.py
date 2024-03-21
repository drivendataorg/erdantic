import logging
from pathlib import Path
import re

from typer.testing import CliRunner

from erdantic.cli import app

logger = logging.getLogger("mkdocs")
runner = CliRunner(mix_stderr=False)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _read_readme():
    readme_path = REPO_ROOT / "README.md"
    logger.info("Reading README from %s", readme_path)
    readme_text = readme_path.read_text()
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
    result = runner.invoke(app, ["--help"], prog_name="erdantic")
    help_text = result.stdout
    return markdown.replace("{{INJECT CLI HELP}}", help_text)


def on_page_markdown(markdown, page, **kwargs):
    if page.title == "CLI Help":
        return _inject_cli_help(markdown)
    return None
