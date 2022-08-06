"""Data transformation helpers."""


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
