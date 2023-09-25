# pylint: disable=no-name-in-module
"""Compatibility shims for Python and Towncrier matrix."""


try:
    # Towncrier >= 22.8.0rc1
    # pylint: disable-next=unused-import
    from towncrier._settings.load import (  # noqa: WPS433
        ConfigError as TowncrierConfigError,
    )
except ImportError:
    # Towncrier < 22.8.0rc1
    try:  # noqa: WPS505
        # Towncrier >= 19.9.0
        from towncrier._settings import (  # noqa: WPS433, WPS440
            ConfigError as TowncrierConfigError,
        )
    except ImportError:
        # Towncrier < 19.9.0
        TowncrierConfigError = ValueError  # noqa: WPS440
