"""The Sphinx extension interface module tests."""

import subprocess  # noqa: S404
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Optional, Set

import pytest

from sphinx.config import Config as SphinxConfig

from sphinxcontrib.towncrier.ext import (
    _get_draft_version_fallback, _resolve_working_directory,
)


release_sentinel = object()
version_sentinel = object()

UTF8_ENCODING = 'utf-8'

CONF_PY_DIR_NAME = 'conf'
CWD_DIR_NAME = 'cwd'
PROJECT_DIR_NAME = 'project'


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


@pytest.mark.parametrize(
    'working_dir',
    (None, Path(__file__).parent),
    ids=('unset', 'absolute'),
)
def test_non_relative_working_dir_kept(
        working_dir: Optional[Path],
        tmp_path: Path,
) -> None:
    """Check that only relative working directories are resolved."""
    config = SimpleNamespace(towncrier_draft_working_directory=working_dir)
    _resolve_working_directory(
        SimpleNamespace(confdir=str(tmp_path)),  # type: ignore[arg-type]
        config,  # type: ignore[arg-type]
    )
    assert config.towncrier_draft_working_directory is working_dir


@pytest.mark.parametrize(
    ('config_locations', 'expected_location'),
    (
        pytest.param(
            {CONF_PY_DIR_NAME, CWD_DIR_NAME},
            CONF_PY_DIR_NAME,
            id='config-in-both',
        ),
        pytest.param(
            {CONF_PY_DIR_NAME},
            CONF_PY_DIR_NAME,
            id='config-near-conf.py',
        ),
        pytest.param(
            {CWD_DIR_NAME},
            CWD_DIR_NAME,
            id='deprecated-cwd-fallback',
        ),
        pytest.param(set(), CONF_PY_DIR_NAME, id='no-config'),
    ),
)
def test_relative_working_dir_resolved(
        caplog: pytest.LogCaptureFixture,
        config_locations: Set[str],
        expected_location: str,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
) -> None:
    """Check that relative working dirs prefer the ``conf.py`` dir."""
    for location in (CONF_PY_DIR_NAME, CWD_DIR_NAME):
        (tmp_path / location / PROJECT_DIR_NAME).mkdir(parents=True)
    for config_location in config_locations:
        project_path = tmp_path / config_location / PROJECT_DIR_NAME
        (project_path / 'towncrier.toml').touch()
    monkeypatch.chdir(tmp_path / CWD_DIR_NAME)

    app = SimpleNamespace(confdir=str(tmp_path / CONF_PY_DIR_NAME))
    config = SimpleNamespace(
        towncrier_draft_config_path=None,
        towncrier_draft_working_directory=PROJECT_DIR_NAME,
    )
    _resolve_working_directory(
        app,  # type: ignore[arg-type]
        config,  # type: ignore[arg-type]
    )

    expected_path = tmp_path / expected_location / PROJECT_DIR_NAME
    assert config.towncrier_draft_working_directory == str(expected_path)
    assert ('deprecated' in caplog.text) is (expected_location == CWD_DIR_NAME)


def test_working_dir_relative_to_conf_py(tmp_path: Path) -> None:
    """Check that a relative path works with Sphinx run elsewhere."""
    (tmp_path / 'docs').mkdir()
    (tmp_path / 'newsfragments').mkdir()
    project_files = {
        'docs/conf.py': (
            "extensions = ['sphinxcontrib.towncrier.ext']\n"
            "towncrier_draft_autoversion_mode = 'draft'\n"
            "towncrier_draft_working_directory = '..'\n"
        ),
        'docs/index.rst': (
            'Changelog\n=========\n\n.. towncrier-draft-entries::\n'
        ),
        'towncrier.toml': '[tool.towncrier]\ndirectory = "newsfragments"',
        'newsfragments/1.feature': 'A sentinel change note',
    }
    for file_name, file_content in project_files.items():
        (tmp_path / file_name).write_text(file_content, encoding=UTF8_ENCODING)

    subprocess.check_call(  # noqa: S603
        (sys.executable, '-m', 'sphinx', '-b', 'html', '-q', 'docs', 'html'),
        cwd=tmp_path,
    )

    html_output = (tmp_path / 'html' / 'index.html').read_text(
        encoding=UTF8_ENCODING,
    )
    assert 'A sentinel change note' in html_output
