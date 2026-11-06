"""Shared fixtures for the whole test suite."""

from pathlib import Path
from types import MappingProxyType
from typing import Iterator, Mapping, Optional, Protocol

import pytest

from sphinxcontrib.towncrier._fragment_discovery import (  # noqa: WPS436
    lookup_towncrier_fragments,
)
from sphinxcontrib.towncrier.ext import (  # noqa: WPS436
    _get_changelog_draft_entries,
)


pytest_plugins = ('sphinx.testing.fixtures',)


CHANGE_NOTES_DIR_NAME = 'change-notes'

TEXT_ENCODING = 'utf-8'

DEFAULT_FRAGMENT_NAME = '1.feature.rst'
DEFAULT_FRAGMENT_TEXT = 'Added a shiny new thing.'

DEFAULT_FRAGMENTS: Mapping[str, str] = MappingProxyType({
    DEFAULT_FRAGMENT_NAME: DEFAULT_FRAGMENT_TEXT,
})

TOWNCRIER_CONFIG = f"""\
[tool.towncrier]
directory = "{CHANGE_NOTES_DIR_NAME}"
name = "test-project"
"""

CONF_PY_TEMPLATE = """\
extensions = ['sphinxcontrib.towncrier.ext']
exclude_patterns = ['_build']
towncrier_draft_working_directory = {working_dir!r}
{extra_settings}
"""

INDEX_RST_TEMPLATE = """\
Changelog
=========

.. towncrier-draft-entries::{directive_content}
"""


def drop_towncrier_memoization() -> None:
    """Forget the Towncrier lookups memoized by the extension.

    Every real-world ``sphinx-build`` invocation starts with cold
    caches. Tests building the same project more than once have to
    emulate that explicitly.
    """
    lookup_towncrier_fragments.cache_clear()
    _get_changelog_draft_entries.cache_clear()


class SphinxProjectMaker(Protocol):  # pylint: disable=too-few-public-methods
    """Call signature of the ``make_sphinx_project`` fixture."""

    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def __call__(  # noqa: WPS211
            self,
            fragments: Mapping[str, str] = ...,
            extra_settings: str = ...,
            directive_content: str = ...,
            towncrier_config: Optional[str] = ...,
            towncrier_config_name: str = ...,
    ) -> Path:
        """Materialize a Sphinx project and return its source dir."""


@pytest.fixture(autouse=True)
def _drop_towncrier_memoization() -> Iterator[None]:
    """Isolate the memoized Towncrier lookups between the tests."""
    drop_towncrier_memoization()
    yield
    drop_towncrier_memoization()


@pytest.fixture
def make_sphinx_project(tmp_path: Path) -> SphinxProjectMaker:
    """Return a factory making throwaway Sphinx + Towncrier projects."""
    def _make_sphinx_project(  # noqa: WPS211, WPS430
            fragments: Mapping[str, str] = DEFAULT_FRAGMENTS,
            extra_settings: str = '',
            directive_content: str = '',
            towncrier_config: Optional[str] = TOWNCRIER_CONFIG,
            towncrier_config_name: str = 'towncrier.toml',
    ) -> Path:
        project_dir = tmp_path / 'project'
        change_notes_dir = project_dir / CHANGE_NOTES_DIR_NAME
        change_notes_dir.mkdir(parents=True)

        if towncrier_config is not None:
            (project_dir / towncrier_config_name).write_text(
                towncrier_config, encoding=TEXT_ENCODING,
            )

        for fragment_name, fragment_text in fragments.items():
            (change_notes_dir / fragment_name).write_text(
                f'{fragment_text}\n', encoding=TEXT_ENCODING,
            )

        srcdir = project_dir / 'docs'
        srcdir.mkdir()
        (srcdir / 'conf.py').write_text(
            CONF_PY_TEMPLATE.format(
                working_dir=str(project_dir),
                extra_settings=extra_settings,
            ),
            encoding=TEXT_ENCODING,
        )
        (srcdir / 'index.rst').write_text(
            INDEX_RST_TEMPLATE.format(
                directive_content=(
                    f'\n\n   {directive_content}' if directive_content else ''
                ),
            ),
            encoding=TEXT_ENCODING,
        )
        return srcdir

    return _make_sphinx_project
