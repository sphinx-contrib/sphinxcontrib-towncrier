"""Cross-Python compatibility helpers."""

import sys
from typing import Iterable


if sys.version_info >= (3, 8):
    from importlib.metadata import (  # noqa: WPS433
        version as importlib_metadata_get_version,
    )
    from shlex import join as shlex_join  # noqa: WPS433
else:
    # Python 3.7 and lower:
    from shlex import quote as _shlex_quote  # noqa: WPS433

    # pylint: disable-next=line-too-long
    from importlib_metadata import (  # type: ignore[no-redef, unused-ignore]  # noqa: LN002, WPS433, WPS440  # `unused-ignore` is only needed under Python 3.6
        version as importlib_metadata_get_version,
    )

    def shlex_join(split_command: Iterable[str]) -> str:  # noqa: WPS440
        """Return a shell-escaped string from *split_command*."""
        return ' '.join(_shlex_quote(arg) for arg in split_command)


__all__ = ('importlib_metadata_get_version', 'shlex_join')  # noqa: WPS410
