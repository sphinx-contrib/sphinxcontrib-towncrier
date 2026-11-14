"""The Sphinx extension interface module tests."""

from pathlib import Path
from types import SimpleNamespace
from typing import List

import pytest

from sphinx.config import Config as SphinxConfig

from sphinxcontrib.towncrier._data_transformers import (
    definition_list_from_pairs,
)
from sphinxcontrib.towncrier.ext import (
    TowncrierFragmentCategoriesDirective, _get_draft_version_fallback,
)


TOWNCRIER_TOML_FILENAME = 'towncrier.toml'
UTF8_ENCODING = 'utf-8'


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


def testdefinition_list_from_pairs() -> None:
    """Check that the pairs turn into terms and their definitions."""
    definition_list = definition_list_from_pairs(
        (('bugfix', 'Bugfixes'), ('feature', 'Features')),
    )
    rendered_pairs = [
        tuple(node.astext() for node in definition_list_item.children)
        for definition_list_item in definition_list.children
    ]
    assert rendered_pairs == [('bugfix', 'Bugfixes'), ('feature', 'Features')]


def _make_categories_directive_stub(
        working_dir: Path,
        noted_dependencies: List[str],
) -> SimpleNamespace:
    """Compose a minimal stand-in for the categories directive."""
    sphinx_config_stub = SimpleNamespace(
        towncrier_draft_working_directory=str(working_dir),
        towncrier_draft_config_path=TOWNCRIER_TOML_FILENAME,
    )
    return SimpleNamespace(
        name='towncrier-fragment-categories',
        env=SimpleNamespace(
            config=sphinx_config_stub,
            note_dependency=noted_dependencies.append,
        ),
        error=RuntimeError,
    )


def test_categories_directive_run(tmp_path: Path) -> None:
    """Check that the directive renders the configured categories."""
    config_file_path = tmp_path / TOWNCRIER_TOML_FILENAME
    config_file_path.write_text(
        '[tool.towncrier]\n'
        '[[tool.towncrier.type]]\n'
        'directory = "bugfix"\n'
        'name = "Bugfixes"\n'
        'showcontent = true\n',
        encoding=UTF8_ENCODING,
    )
    noted_dependencies: List[str] = []

    rendered_nodes = TowncrierFragmentCategoriesDirective.run(
        _make_categories_directive_stub(  # type: ignore[arg-type]
            tmp_path, noted_dependencies,
        ),
    )

    assert noted_dependencies == [str(config_file_path)]
    assert rendered_nodes[0].astext() == 'bugfix\n\nBugfixes'


def test_categories_directive_run_no_cfg(tmp_path: Path) -> None:
    """Check that an unreadable config makes the directive error out."""
    noted_dependencies: List[str] = []
    expected_error_msg = (
        '^Error in "towncrier-fragment-categories" directive: '
        r'unable to look up the Towncrier change note categories\.$'
    )

    with pytest.raises(RuntimeError, match=expected_error_msg):
        TowncrierFragmentCategoriesDirective.run(
            _make_categories_directive_stub(  # type: ignore[arg-type]
                tmp_path, noted_dependencies,
            ),
        )

    assert not noted_dependencies
