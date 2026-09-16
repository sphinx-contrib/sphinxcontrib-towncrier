"""Data transformation helpers."""

from typing import Iterable, Tuple, Union


def escape_project_version_rst_substitution(version: str) -> str:
    """Prepend an escaped whitespace before RST substitution."""
    if not version.startswith('|') or version.count('|') <= 1:
        return version

    # A corner case exists when the towncrier config has something like
    # `v{version}` in the title format **and** the directive target
    # argument starts with a substitution like `|release|`. And so
    # when combined, they produce a v|release|` causing RST to not
    # substitute the `|release|` part. But adding an escaped space
    # solves this: that escaped space renders as an empty string and
    # the substitution gets processed properly so the result would
    # be something like `v1.0` as expected.
    return rf'\ {version}'


def normalize_empty_markers(
        markers: Union[str, Iterable[str]],
) -> Tuple[str, ...]:
    """Turn the configured empty-changelog markers into a tuple.

    A bare string is wrapped rather than iterated: iterating it would
    match single characters against the Towncrier output, silently
    swallowing non-empty changelogs.
    """
    return (markers, ) if isinstance(markers, str) else tuple(markers)
