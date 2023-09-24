"""Version definition."""

try:
    # pylint: disable=unused-import
    from ._scm_version import version as __version__  # noqa: WPS433, WPS436
except ImportError:
    from ._compat import importlib_metadata_get_version  # noqa: WPS433, WPS436

    __version__ = importlib_metadata_get_version(  # noqa: WPS440
        'sphinxcontrib-towncrier',
    )
