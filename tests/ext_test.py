"""The Sphinx extension interface module tests."""

import sys
from pathlib import Path

import pytest

from sphinx.config import Config as SphinxConfig

from sphinxcontrib.towncrier.ext import (
    _get_changelog_draft_entries, _get_draft_version_fallback,
)


release_sentinel = object()
version_sentinel = object()


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


@pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason='`python -P` is only available under Python 3.11+',
)
def test_draft_ignores_source_checkout_on_path(
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
) -> None:
    """Check that Towncrier imports the installed package.

    The source checkout in the working directory may be unimportable,
    for example, when its C-extensions are not compiled.
    """
    installed_pkg_dir = tmp_path / 'site-packages' / 'pkg'
    source_pkg_dir = tmp_path / 'checkout' / 'pkg'
    installed_pkg_dir.mkdir(parents=True)
    (installed_pkg_dir / '__init__.py').touch()
    (source_pkg_dir / 'newsfragments').mkdir(parents=True)
    (source_pkg_dir / '__init__.py').write_text(
        "raise ImportError('C-extensions are not compiled')\n",
    )
    (source_pkg_dir.parent / 'pyproject.toml').write_text(
        "[tool.towncrier]\npackage = 'pkg'\n",
    )
    monkeypatch.setenv('PYTHONPATH', str(installed_pkg_dir.parent))

    changelog_draft = _get_changelog_draft_entries.__wrapped__(
        '1.0',
        allow_empty=True,
        working_dir=str(source_pkg_dir.parent),
    )
    assert 'Pkg 1.0' in changelog_draft
