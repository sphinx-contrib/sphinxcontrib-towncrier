"""Towncrier config reader tests."""


import os

import pytest

from towncrier._settings.load import ConfigError

from sphinxcontrib.towncrier._towncrier import get_towncrier_config


def test_towncrier_config_section_missing(tmp_path):
    """Test config file without Towncrier section raises an error."""
    expected_error_msg = r'^No \[tool\.towncrier\] section\.$'

    with pytest.raises(ConfigError, match=expected_error_msg):
        get_towncrier_config(tmp_path, os.devnull)


@pytest.mark.parametrize(
    'config_file_name',
    (
        None,
        pytest.param('', id='<empty-string>'),
        'pyproject.toml',
        'towncrier.toml',
    ),
)
def test_towncrier_config_file_missing(config_file_name, monkeypatch, tmp_path):
    """Test missing Towncrier config file raises an error."""
    tmp_working_dir_path = tmp_path / 'working-directory'
    tmp_working_dir_path.mkdir()
    monkeypatch.chdir(tmp_working_dir_path)

    expected_error_msg = (
        fr"^\[Errno 2\] No such file or directory: '{config_file_name}'$"
    )

    with pytest.raises(FileNotFoundError, match=expected_error_msg):
        get_towncrier_config(tmp_path, config_file_name)
