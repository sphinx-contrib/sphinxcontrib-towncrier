"""Version definition."""

try:
    # pylint: disable=unused-import
    from ._scm_version import version as __version__  # noqa: WPS433, WPS436
except ImportError:
    from importlib.metadata import (  # noqa: WPS433, WPS436
        version as importlib_metadata_get_version,
    )

    __version__ = importlib_metadata_get_version(  # noqa: WPS440
        'sphinxcontrib-towncrier',
    )
