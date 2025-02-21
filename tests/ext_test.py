"""The Sphinx extension interface module tests."""

import pytest

from sphinx.config import Config as SphinxConfig

from sphinxcontrib.towncrier.ext import _get_draft_version_fallback


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
