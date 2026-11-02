"""Towncrier config reader tests."""


import zipfile
from importlib.metadata import version as _get_installed_project_version
from pathlib import Path
from typing import Union

import pytest

from towncrier._settings.load import Config  # noqa: WPS436

from sphinxcontrib.towncrier._towncrier import (
    get_towncrier_config, get_towncrier_template_path,
)


_TOWNCRIER_VERSION = _get_installed_project_version('towncrier')
_TOWNCRIER_RELEASED_POST_2025_INCLUSIVE = int(  # noqa: WPS114
    _TOWNCRIER_VERSION.split('.', 1)[0],
) >= 25  # noqa: WPS432


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

    expected_error_msg = (
        '^Towncrier was unable to load the configuration from file '
        fr'`{empty_config_file !s}`: No \[tool\.towncrier\] section\.$'
    )

    if _TOWNCRIER_RELEASED_POST_2025_INCLUSIVE:
        assert isinstance(
            get_towncrier_config(tmp_path, empty_config_file),
            Config,
        )
        return

    with pytest.raises(LookupError, match=expected_error_msg):
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
        '^Towncrier was unable to load the configuration from file '
        f'`{config_file_name !s}`: '
        fr"\[Errno 2\] No such file or directory: '{config_file_name !s}'$"
    )

    with pytest.raises(LookupError, match=expected_error_msg):
        get_towncrier_config(tmp_path, config_file_name)


def _load_config_with_template(tmp_path: Path, template: str) -> Config:
    config_file_path = tmp_path / 'towncrier.toml'
    config_file_path.write_text(
        f'[tool.towncrier]\ntemplate = {template !r}',
        encoding='utf-8',
    )
    return get_towncrier_config(tmp_path, config_file_path)


def test_towncrier_template_path_file(tmp_path: Path) -> None:
    """Test that a template file path is returned."""
    template_path = tmp_path / 'template.j2'
    template_path.write_text('', encoding='utf-8')
    towncrier_config = _load_config_with_template(tmp_path, template_path.name)

    assert get_towncrier_template_path(towncrier_config) == template_path


def test_towncrier_template_path_package_resource(tmp_path: Path) -> None:
    """Test that a template in an on-disk package is returned."""
    towncrier_config = _load_config_with_template(
        tmp_path, 'towncrier:default',
    )

    template_path = get_towncrier_template_path(towncrier_config)

    assert template_path is not None
    assert template_path.name == 'default.rst'
    assert template_path.is_file()


def test_towncrier_template_path_zipped_package(
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
) -> None:
    """Test that a template in a zip-imported package is not returned."""
    towncrier_config = _load_config_with_template(
        tmp_path, 'towncrier:default',
    )
    zip_archive_path = tmp_path / 'package.zip'
    with zipfile.ZipFile(zip_archive_path, 'w') as zip_archive:
        zip_archive.writestr('default.rst', '')
    monkeypatch.setattr(
        'sphinxcontrib.towncrier._towncrier._get_package_resources',
        lambda _package_name: zipfile.Path(zip_archive_path),
    )

    assert get_towncrier_template_path(towncrier_config) is None
