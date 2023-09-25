"""Compatibility shims for Python and Towncrier matrix."""


try:
    from towncrier._settings.load import (  # noqa: WPS433
        ConfigError as TowncrierConfigError,
    )
except ImportError:
    from towncrier._settings import (  # noqa: F401, WPS433, WPS440
        ConfigError as TowncrierConfigError,
    )
