"""The Sphinx extension interface module tests."""

import logging
from typing import Any

import pytest

from sphinx.config import Config as SphinxConfig

from sphinxcontrib.towncrier.ext import (
    _get_draft_version_fallback, _warn_on_missing_version_title,
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


@pytest.mark.parametrize(
    ('expected_version', 'draft_markup_source'),
    (
        pytest.param(
            '1.2.3', '1.2.3 (2021-01-01)\n==================',
            id='rst-title-rendered-by-template',
        ),
        pytest.param(
            '1.2.3', 'Release v1.2.3\n==============',
            id='version-embedded-into-custom-title-format',
        ),
        pytest.param(
            r'\ |release|', r'\ |release| (2021-01-01)',
            id='escaped-rst-substitution',
        ),
        pytest.param(
            '', 'Bugfixes\n--------\n\n- Some change.',
            id='empty-version-never-warns',
        ),
    ),
)
def test__warn_on_missing_version_title_quiet(  # noqa: WPS116, WPS118
        expected_version: str,
        draft_markup_source: str,
        caplog: pytest.LogCaptureFixture,
) -> None:
    """Check that a rendered version title produces no warning."""
    with caplog.at_level(logging.WARNING):
        _warn_on_missing_version_title(
            expected_version, draft_markup_source,
        )

    assert not caplog.records


def test__warn_on_missing_version_title_warns(  # noqa: WPS116, WPS118
        caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify that a title-less draft yields a suppressible warning."""
    with caplog.at_level(logging.WARNING):
        _warn_on_missing_version_title(
            '[UNRELEASED DRAFT]',
            'Bugfixes\n--------\n\n- Some change. (#1)',
            location='changelog:12',
        )

    assert len(caplog.records) == 1

    # Sphinx attaches its extras to the record dynamically, hence `Any`:
    emitted_warning: Any = caplog.records[-1]
    assert emitted_warning.levelno == logging.WARNING
    assert "'[UNRELEASED DRAFT]'" in emitted_warning.getMessage()
    assert emitted_warning.location == 'changelog:12'
    # The category lets users silence it via `suppress_warnings`:
    assert (emitted_warning.type, emitted_warning.subtype) == (
        'towncrier', 'missing-version-title',
    )
