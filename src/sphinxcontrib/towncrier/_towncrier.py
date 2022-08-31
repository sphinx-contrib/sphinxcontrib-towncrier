"""Towncrier related shims."""

from pathlib import Path
from typing import Any, Dict


try:
    # Towncrier >= 22.8.0rc1
    # pylint: disable=import-error,no-name-in-module
    from towncrier._settings.load import (  # noqa: WPS433, WPS436
        load_config_from_file,
    )
except ImportError:
    # pylint: disable=import-error,no-name-in-module
    from towncrier._settings import (  # noqa: WPS433, WPS436, WPS440
        load_config_from_file,
    )


def get_towncrier_config(
        project_path: Path,
        final_config_path: Path,
) -> Dict[str, Any]:  # FIXME: add a better type  # pylint: disable=fixme
    """Return the towncrier config dictionary."""
    try:
        # Towncrier >= 19.9.0
        return load_config_from_file(str(project_path), str(final_config_path))
    except TypeError:
        # Towncrier < 19.9.0
        return load_config_from_file(str(final_config_path))
