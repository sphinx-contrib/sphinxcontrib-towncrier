"""Unit tests of the extension bits."""
import sys

import pytest

from sphinxcontrib.towncrier._compat import shlex_join
from sphinxcontrib.towncrier.ext import (
    _find_config_file, _get_changelog_draft_entries,
)


NO_OUTPUT_MARKER = r'\[No output\]'
PYPROJECT_TOML_FILENAME = 'pyproject.toml'
TOWNCRIER_TOML_FILENAME = 'towncrier.toml'


_get_changelog_draft_entries_unwrapped = (
    _get_changelog_draft_entries.
    __wrapped__  # So that the non-cached function version is tested
)


@pytest.mark.parametrize(
    ('failing_cmd', 'stdout_msg', 'stderr_msg'),
    (
        (
            (
                'false',
            ),
            NO_OUTPUT_MARKER,
            NO_OUTPUT_MARKER,
        ),
        (
            (
                sys.executable,
                '-c',
                r'print("test standard output\nsecond line");'
                'raise SystemExit(1)',
            ),
            r'test standard output\nsecond line\n',
            NO_OUTPUT_MARKER,
        ),
        (
            (
                sys.executable,
                '-c',
                r'raise SystemExit("test standard error\nsecond line")',
            ),
            NO_OUTPUT_MARKER,
            r'test standard error\nsecond line',
        ),
        (
            (
                sys.executable,
                '-c',
                r'print("test standard output\nsecond line out");'
                r'raise SystemExit("test standard error\nsecond line err")',
            ),
            r'test standard output\nsecond line out\n',
            r'test standard error\nsecond line err',
        ),
    ),
    ids=(
        'no stdout, no stderr',
        'stdout, no stderr',
        'no stdout, stderr',
        'stdout, stderr',
    ),
)
def test_towncrier_draft_generation_failure_msg(
        failing_cmd, stdout_msg, stderr_msg,
        monkeypatch,
) -> None:
    """Test that a failing command produces a :class:`RuntimeError`."""
    version_string = 'test version'

    monkeypatch.setattr(
        'sphinxcontrib.towncrier.ext.TOWNCRIER_DRAFT_CMD',
        failing_cmd,  # So that the invoked command would return a failure
    )

    escaped_failing_cmd = (  # This is necessary because it's used in a regexp
        shlex_join(failing_cmd).
        replace('\\', r'\\').
        replace('(', r'\(').
        replace(')', r'\)')
    )
    expected_return_code = 1
    expected_error_message = (
        '^'  # noqa: WPS221
        'Command exited unexpectedly.\n\n'
        rf"Command: {escaped_failing_cmd} --version '{version_string}'\n"
        f'Return code: {expected_return_code}\n\n'
        'Standard output:\n'
        f'{stdout_msg}\n\n'
        'Standard error:\n'
        f'{stderr_msg}'
        '$'
    )

    with pytest.raises(RuntimeError, match=expected_error_message):
        _get_changelog_draft_entries_unwrapped(version_string)


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
def test_find_config_files(
        config_file_names_on_disk,
        expected_config_file_name,
        tmp_path,
) -> None:
    """Verify that the correct Towncrier config is always preferred."""
    for config_file_name_on_disk in config_file_names_on_disk:
        tmp_path.joinpath(config_file_name_on_disk).write_text(
            '', encoding='utf-8',
        )

    assert _find_config_file(tmp_path).name == expected_config_file_name
