"""The Sphinx extension interface module tests."""

import os
import subprocess  # noqa: S404
import sys
from pathlib import Path

import pytest

from sphinx.config import Config as SphinxConfig

from sphinxcontrib.towncrier.ext import _get_draft_version_fallback


release_sentinel = object()
version_sentinel = object()

UTF8_ENCODING = 'utf-8'


@pytest.fixture
def sphinx_config() -> SphinxConfig:
    """Initialize a Sphinx config stub for testing."""
    return SphinxConfig(
        overrides={'release': release_sentinel, 'version': version_sentinel},
    )


@pytest.mark.parametrize(
    ('autoversion_mode', 'expected_version'),
    (
        ('sphinx-release', release_sentinel),
        ('sphinx-version', version_sentinel),
        ('draft', '[UNRELEASED DRAFT]'),
    ),
)
def test__get_draft_version_fallback_known_strategy(  # noqa: WPS116, WPS118
        autoversion_mode: str,
        expected_version: object,
        sphinx_config: SphinxConfig,
) -> None:
    """Check that valid strategies source correct values."""
    computed_version = _get_draft_version_fallback.__wrapped__(
        autoversion_mode,
        sphinx_config,
    )
    assert computed_version == expected_version


@pytest.mark.parametrize('autoversion_mode', ('blah', '', 'v1.0'))
def test__get_draft_version_fallback_invalid_strategy(  # noqa: WPS116, WPS118
        autoversion_mode: str,
        sphinx_config: SphinxConfig,
) -> None:
    """Ensure invalid strategy yields an exception."""
    expected_error_msg = (
        '^Expected "strategy" to be one of '
        r"{'[\w,\s'-]+'} "
        f'but got {autoversion_mode !r}$'
    )
    with pytest.raises(ValueError, match=expected_error_msg):
        _get_draft_version_fallback.__wrapped__(
            autoversion_mode,
            sphinx_config,
        )


def _build_html_docs(project_path: Path) -> Path:
    """Run an incremental Sphinx build and return the doctree path."""
    output_path = project_path / 'html'
    subprocess.check_call(  # noqa: S603
        (
            sys.executable, '-m', 'sphinx',
            '-b', 'html', '-q',
            str(project_path / 'docs'), str(output_path),
        ),
    )
    return output_path / '.doctrees' / 'index.doctree'


def test_removed_fragment_rebuilds_doc_once(tmp_path: Path) -> None:
    """Check that a removed fragment only causes a single doc re-read."""
    (tmp_path / 'docs').mkdir()
    (tmp_path / 'newsfragments').mkdir()
    project_files = {
        'docs/conf.py': (
            'import pathlib\n'
            "extensions = ['sphinxcontrib.towncrier.ext']\n"
            "towncrier_draft_autoversion_mode = 'draft'\n"
            'towncrier_draft_working_directory = '
            'pathlib.Path(__file__).parents[1]\n'
        ),
        'docs/index.rst': (
            'Changelog\n=========\n\n.. towncrier-draft-entries::\n'
        ),
        'towncrier.toml': '[tool.towncrier]\ndirectory = "newsfragments"',
        'newsfragments/1.feature': 'A kept change note',
        'newsfragments/2.feature': 'A removed change note',
    }
    for file_name, file_content in project_files.items():
        (tmp_path / file_name).write_text(file_content, encoding=UTF8_ENCODING)
    _build_html_docs(tmp_path)

    (tmp_path / 'newsfragments' / '2.feature').unlink()
    doctree_path = _build_html_docs(tmp_path)
    # Backdate the doctree to detect it being re-written by the next build
    os.utime(doctree_path, (0, 0))
    _build_html_docs(tmp_path)

    assert doctree_path.stat().st_mtime == 0
