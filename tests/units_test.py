"""Unit tests of the extension bits."""

import json
import shlex
import sys
import typing

import pytest

from sphinxcontrib.towncrier.ext import _get_changelog_draft_entries


NO_OUTPUT_MARKER = r'\[No output\]'
PYTHON_INLINE_SNIPPET_CMD_FLAG = '-c'


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
                PYTHON_INLINE_SNIPPET_CMD_FLAG,
                r'print("test standard output\nsecond line");'
                'raise SystemExit(1)',
            ),
            r'test standard output\nsecond line\n',
            NO_OUTPUT_MARKER,
        ),
        (
            (
                sys.executable,
                PYTHON_INLINE_SNIPPET_CMD_FLAG,
                r'raise SystemExit("test standard error\nsecond line")',
            ),
            NO_OUTPUT_MARKER,
            r'test standard error\nsecond line',
        ),
        (
            (
                sys.executable,
                PYTHON_INLINE_SNIPPET_CMD_FLAG,
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
        failing_cmd: typing.Tuple[str], stdout_msg: str, stderr_msg: str,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that a failing command produces a :class:`RuntimeError`."""
    version_string = 'test version'

    monkeypatch.setattr(
        'sphinxcontrib.towncrier.ext.TOWNCRIER_DRAFT_CMD',
        failing_cmd,  # So that the invoked command would return a failure
    )

    escaped_failing_cmd = (  # This is necessary because it's used in a regexp
        shlex.join(failing_cmd).
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


def test_towncrier_draft_generation_with_config(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test explicit config gets passed into Towncrier."""
    monkeypatch.setattr(
        'sphinxcontrib.towncrier.ext.TOWNCRIER_DRAFT_CMD',
        (
            sys.executable,
            '-I',
            PYTHON_INLINE_SNIPPET_CMD_FLAG,
            'import json, sys; print(json.dumps(sys.argv))',
        ),
    )

    argv_json = _get_changelog_draft_entries_unwrapped(
        'test version',
        config_path='sentinel-config-path',
    )
    computed_proc_args = json.loads(argv_json)
    computed_towncrier_args = computed_proc_args[3:]

    assert computed_towncrier_args == ['--config', 'sentinel-config-path']


def test_towncrier_draft_generation_with_empty_cl(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that empty change log triggers an exception."""
    monkeypatch.setattr(
        'sphinxcontrib.towncrier.ext.TOWNCRIER_DRAFT_CMD',
        (
            sys.executable,
            '-I',
            PYTHON_INLINE_SNIPPET_CMD_FLAG,
            'print("No significant changes")',
        ),
    )

    expected_error_message = (
        '^There are no unreleased changelog entries so far$'
    )
    with pytest.raises(LookupError, match=expected_error_message):
        _get_changelog_draft_entries_unwrapped(
            'test version',
            allow_empty=False,
        )
