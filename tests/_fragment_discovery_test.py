"""Unit tests of the fragment discovery logic."""


from pathlib import Path
from typing import Set, Union

import pytest

from sphinxcontrib.towncrier._fragment_discovery import (
    _find_config_file, _resolve_spec_config, lookup_towncrier_fragments,
)


PYPROJECT_TOML_FILENAME = 'pyproject.toml'
TOWNCRIER_TOML_FILENAME = 'towncrier.toml'


@pytest.mark.parametrize(
    ('config_file_names_on_disk', 'expected_config_file_name'),
    (
        pytest.param(
            set(),
            PYPROJECT_TOML_FILENAME,
            id='pyproject.toml-when-no-configs',
        ),
        pytest.param(
            {PYPROJECT_TOML_FILENAME},
            'pyproject.toml',
            id='pyproject.toml-only',
        ),
        pytest.param(
            {TOWNCRIER_TOML_FILENAME},
            TOWNCRIER_TOML_FILENAME,
            id='towncrier.toml-only',
        ),
        pytest.param(
            {PYPROJECT_TOML_FILENAME, TOWNCRIER_TOML_FILENAME},
            TOWNCRIER_TOML_FILENAME,
            id='towncrier.toml-over-pyproject.toml',
        ),
    ),
)
def test_find_config_file(
        config_file_names_on_disk: Set[str],
        expected_config_file_name: str,
        tmp_path: Path,
) -> None:
    """Verify that the correct Towncrier config is always preferred."""
    for config_file_name_on_disk in config_file_names_on_disk:
        tmp_path.joinpath(config_file_name_on_disk).write_text(
            '', encoding='utf-8',
        )

    assert _find_config_file(tmp_path).name == expected_config_file_name


@pytest.mark.parametrize(
    ('base_path', 'config_path', 'resolved_path'),
    (
        (
            Path('sentinel-path'),
            'towncrier.toml',
            Path('sentinel-path/towncrier.toml'),
        ),
        (Path('sentinel-path'), None, None),
    ),
    ids=('explicit-config-path', 'unset-config-path'),
)
def test_resolve_spec_config(
        base_path: Path,
        config_path: Union[str, None],
        resolved_path: Union[Path, None],
) -> None:
    """Verify that config path is resolved properly."""
    assert _resolve_spec_config(base_path, config_path) == resolved_path


def test_lookup_towncrier_fragments_missing_cfg(tmp_path: Path) -> None:
    """Test that missing config file causes zero fragment set."""
    discovered_fragment_paths = lookup_towncrier_fragments.__wrapped__(
        tmp_path,
        'blah.toml',
    )
    assert discovered_fragment_paths == set()
