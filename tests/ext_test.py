"""The Sphinx extension interface module tests."""

from typing import Any, Dict

import pytest

from sphinx.config import Config as SphinxConfig

from sphinxcontrib.towncrier.ext import _get_draft_version_fallback, setup


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


class _ConfigRecordingAppStub:
    """A minimal Sphinx app stand-in recording declared config values."""

    def __init__(self) -> None:
        """Initialize an empty config value default map."""
        self.config_defaults: Dict[str, Any] = {}

    def add_config_value(self, name, default, **_kwargs) -> None:
        """Record the default of one declared config value."""
        self.config_defaults[name] = default

    def add_directive(self, *args) -> None:
        """Ignore the directive registration."""

    def add_env_collector(self, *args) -> None:
        """Ignore the environment collector registration."""


def test_default_autoversion_mode_is_supported(  # noqa: WPS118
        sphinx_config: SphinxConfig,
) -> None:
    """Ensure the shipped default strategy is not rejected."""
    app = _ConfigRecordingAppStub()
    setup(app)
    default_autoversion_mode = app.config_defaults[
        'towncrier_draft_autoversion_mode'
    ]

    computed_version = _get_draft_version_fallback.__wrapped__(
        default_autoversion_mode,
        sphinx_config,
    )
    assert computed_version == '[UNRELEASED DRAFT]'
