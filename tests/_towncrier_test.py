"""Towncrier config reader tests."""


from pathlib import Path
from typing import Union

import pytest

from sphinxcontrib.towncrier._towncrier import get_towncrier_config
from ._compat import TowncrierConfigError


def test_towncrier_config_section_missing(
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
) -> None:
    """Test config file without Towncrier section raises an error."""
    tmp_working_dir_path = tmp_path / 'working-directory'
    tmp_working_dir_path.mkdir()
    empty_config_file = Path('arbitrary-config.toml')
    (tmp_working_dir_path / empty_config_file).touch()
    monkeypatch.chdir(tmp_working_dir_path)

    expected_error_msg = r'^No \[tool\.towncrier\] section\.$'

    with pytest.raises(TowncrierConfigError, match=expected_error_msg):
        get_towncrier_config(tmp_path, empty_config_file)


@pytest.mark.parametrize(
    'config_file_name',
    (
        None,
        Path('pyproject.toml'),
        Path('towncrier.toml'),
    ),
)
def test_towncrier_config_file_missing(
        config_file_name: Union[Path, None],
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
) -> None:
    """Test missing Towncrier config file raises an error."""
    tmp_working_dir_path = tmp_path / 'working-directory'
    tmp_working_dir_path.mkdir()
    monkeypatch.chdir(tmp_working_dir_path)

    expected_error_msg = (
        fr"^\[Errno 2\] No such file or directory: '{config_file_name}'$"
    )

    with pytest.raises(FileNotFoundError, match=expected_error_msg):
        get_towncrier_config(tmp_path, config_file_name)
