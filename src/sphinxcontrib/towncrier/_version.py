"""Version definition."""

try:
    # pylint: disable=unused-import
    from ._scm_version import version as __version__  # noqa: WPS433, WPS436
except ImportError:
    try:  # noqa: WPS505
        from importlib.metadata import (  # Python 3.8+  # noqa: WPS433
            version as _get_version,
        )
    except ImportError:
        from importlib_metadata import (  # noqa: WPS433, WPS440
            version as _get_version,
        )

    __version__ = _get_version('sphinxcontrib-towncrier')  # noqa: WPS440
