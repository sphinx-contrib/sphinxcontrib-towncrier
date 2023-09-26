"""Unit tests of the fragment discovery logic."""


from pathlib import Path
from typing import Set

import pytest

from sphinxcontrib.towncrier._fragment_discovery import _find_config_file


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
