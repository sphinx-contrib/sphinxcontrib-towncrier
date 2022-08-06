"""Cross-Python compatibility helpers."""

import sys
from typing import Iterable


if sys.version_info >= (3, 8):
    from shlex import join as shlex_join  # noqa: WPS433
else:
    # Python 3.7 and lower:
    from shlex import quote as _shlex_quote  # noqa: WPS433

    def shlex_join(split_command: Iterable[str]) -> str:  # noqa: WPS440
        """Return a shell-escaped string from *split_command*."""
        return ' '.join(_shlex_quote(arg) for arg in split_command)


__all__ = ('shlex_join',)  # noqa: WPS410
