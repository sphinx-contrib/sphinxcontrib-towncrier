"""Data transformation tests."""
import pytest

from sphinxcontrib.towncrier._data_transformers import (
    escape_project_version_rst_substitution,
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
def test_escape_version(test_input, escaped_input):
    """Test that the version is escaped before RST substitutions.

    RST substitution as the first item should be escaped. Otherwise,
    the input is expected to remain unchanged.
    """
    assert escape_project_version_rst_substitution(test_input) == escaped_input
