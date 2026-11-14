"""Data transformation tests."""
import typing

import pytest

from sphinxcontrib.towncrier._data_transformers import (
    escape_project_version_rst_substitution, normalize_empty_markers,
)


@pytest.mark.parametrize(
    ('test_input', 'escaped_input'),
    (
        (r'\ |release|', r'\ |release|'),
        ('|release|', r'\ |release|'),
        ('|release', '|release'),
        ('v|release|', 'v|release|'),
    ),
    ids=(
        'substitution already escaped',
        'correct substitution at the beginning',
        'unclosed substitution at the beginning',
        'correct substitution in the middle',
    ),
)
def test_escape_version(test_input: str, escaped_input: str) -> None:
    """Test that the version is escaped before RST substitutions.

    RST substitution as the first item should be escaped. Otherwise,
    the input is expected to remain unchanged.
    """
    assert escape_project_version_rst_substitution(test_input) == escaped_input


@pytest.mark.parametrize(
    ('test_input', 'normalized'),
    (
        ('No significant changes', ('No significant changes', )),
        (['alpha', 'beta'], ('alpha', 'beta')),
        (('gamma', ), ('gamma', )),
        ([], ()),
    ),
    ids=(
        'bare string is wrapped, not iterated',
        'list becomes a tuple',
        'tuple is preserved',
        'empty collection stays empty',
    ),
)
def test_normalize_empty_markers(
        test_input: typing.Union[str, typing.Iterable[str]],
        normalized: typing.Tuple[str, ...],
) -> None:
    """Test that the markers end up as a hashable tuple of strings."""
    assert normalize_empty_markers(test_input) == normalized
