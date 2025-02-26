"""Unit tests of the fragment discovery logic."""


from pathlib import Path
from typing import Set, Union

import pytest

from sphinxcontrib.towncrier._fragment_discovery import (
    _find_config_file, _resolve_spec_config, lookup_towncrier_fragments,
)


PYPROJECT_TOML_FILENAME = 'pyproject.toml'
TOWNCRIER_TOML_FILENAME = 'towncrier.toml'

UTF8_ENCODING = 'utf-8'


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
            '', encoding=UTF8_ENCODING,
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


@pytest.mark.parametrize(
    'chdir',
    (True, False),
    ids=('cwd', 'detached-work-dir'),
)
@pytest.mark.parametrize(
    ('sphinx_configured_path', 'config_file_path'),
    (
        (None, TOWNCRIER_TOML_FILENAME),
        (None, PYPROJECT_TOML_FILENAME),
        (TOWNCRIER_TOML_FILENAME, TOWNCRIER_TOML_FILENAME),
        (PYPROJECT_TOML_FILENAME, PYPROJECT_TOML_FILENAME),
    ),
    ids=(
        'implicit-config-path-pyproject',
        'explicit-config-path-pyproject',
        'implicit-config-path-towncrier',
        'explicit-config-path-towncrier',
    ),
)
def test_lookup_towncrier_fragments(
        chdir: bool,
        config_file_path: str,
        monkeypatch: pytest.MonkeyPatch,
        sphinx_configured_path: Union[str, None],
        tmp_path: Path,
) -> None:
    """Test that fragments can be discovered in configured location."""
    change_notes_dir_base_name = 'newsfragments-sentinel'
    tmp_working_dir_path = tmp_path / 'working-directory'
    change_notes_dir_path = tmp_working_dir_path / change_notes_dir_base_name
    change_note_sentinel_path = change_notes_dir_path / '0.misc.1.rst'

    change_notes_dir_path.mkdir(parents=True)
    change_note_sentinel_path.write_text('sentinel', encoding=UTF8_ENCODING)

    (tmp_working_dir_path / config_file_path).write_text(
        f'[tool.towncrier]\ndirectory={change_notes_dir_base_name !r}',
        encoding=UTF8_ENCODING,
    )

    if chdir:
        monkeypatch.chdir(tmp_working_dir_path)
    discovered_fragment_paths = lookup_towncrier_fragments.__wrapped__(
        None if chdir else tmp_working_dir_path,
        sphinx_configured_path,
    )
    assert discovered_fragment_paths == {change_note_sentinel_path}


def test_lookup_towncrier_fragments_missing_cfg(tmp_path: Path) -> None:
    """Test that missing config file causes zero fragment set."""
    discovered_fragment_paths = lookup_towncrier_fragments.__wrapped__(
        tmp_path,
        'blah.toml',
    )
    assert discovered_fragment_paths == set()


def test_lookup_towncrier_fragments_missing_dir(tmp_path: Path) -> None:
    """Test that missing fragments folder causes zero fragment set."""
    (tmp_path / TOWNCRIER_TOML_FILENAME).write_text(
        '[tool.towncrier]\ndirectory="non/existing/dir"',
        encoding=UTF8_ENCODING,
    )
    discovered_fragment_paths = lookup_towncrier_fragments.__wrapped__(
        tmp_path,
        TOWNCRIER_TOML_FILENAME,
    )
    assert discovered_fragment_paths == set()


def test_lookup_towncrier_fragments_unset_dir(tmp_path: Path) -> None:
    """Test that implicit fragments folder uses defaults."""
    (tmp_path / TOWNCRIER_TOML_FILENAME).write_text(
        '[tool.towncrier]',
        encoding=UTF8_ENCODING,
    )
    discovered_fragment_paths = lookup_towncrier_fragments.__wrapped__(
        tmp_path,
        TOWNCRIER_TOML_FILENAME,
    )
    assert discovered_fragment_paths == set()
