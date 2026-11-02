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


def _build_html_docs(project_path: Path) -> str:
    """Run an incremental Sphinx build and return the rendered page."""
    output_path = project_path / 'html'
    subprocess.check_call(  # noqa: S603
        (
            sys.executable, '-m', 'sphinx',
            '-b', 'html', '-q',
            str(project_path / 'docs'), str(output_path),
        ),
    )
    return (output_path / 'index.html').read_text(encoding=UTF8_ENCODING)


@pytest.mark.parametrize(
    ('changed_file_name', 'changed_file_content'),
    (
        pytest.param(
            'template.j2',
            'SENTINEL-UPDATED',
            id='template-edited',
        ),
        pytest.param(
            'towncrier.toml',
            '[tool.towncrier]\ntemplate = "updated-template.j2"',
            id='config-edited',
        ),
    ),
)
def test_config_change_invalidates_doctree_cache(
        changed_file_name: str,
        changed_file_content: str,
        tmp_path: Path,
) -> None:
    """Check that the draft is re-rendered on Towncrier config changes."""
    (tmp_path / 'docs').mkdir()
    # Older Towncrier versions fail when the change notes dir is missing
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
        'towncrier.toml': '[tool.towncrier]\ntemplate = "template.j2"',
        'template.j2': 'SENTINEL-ORIGINAL',
        'updated-template.j2': 'SENTINEL-UPDATED',
    }
    for file_name, file_content in project_files.items():
        (tmp_path / file_name).write_text(file_content, encoding=UTF8_ENCODING)

    assert 'SENTINEL-ORIGINAL' in _build_html_docs(tmp_path)

    changed_file_path = tmp_path / changed_file_name
    changed_file_path.write_text(changed_file_content, encoding=UTF8_ENCODING)
    # Ensure the change is newer than the doctree cache, regardless of
    # the file system timestamp resolution
    future_timestamp = changed_file_path.stat().st_mtime + 10
    os.utime(changed_file_path, (future_timestamp, future_timestamp))

    assert 'SENTINEL-UPDATED' in _build_html_docs(tmp_path)
