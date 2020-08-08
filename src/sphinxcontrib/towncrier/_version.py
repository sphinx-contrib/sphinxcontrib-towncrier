"""Version definition."""

try:
    from ._scm_version import version as __version__
except ImportError:
    from pkg_resources import get_distribution as _get_dist
    __version__ = _get_dist('sphinxcontrib-towncrier').version
