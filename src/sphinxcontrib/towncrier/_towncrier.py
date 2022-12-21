"""Towncrier related shims."""

from contextlib import suppress as _suppress_exception
from pathlib import Path
from typing import Any, Dict


with _suppress_exception(ImportError):
    # NOTE: This will not raise an exception under Python >= 3.7, and is only
    # NOTE: needed for Towncrier >= 22.12.0rc1 which doesn't support Python 3.6
    from dataclasses import asdict as _dataclass_to_dict  # noqa: WPS433


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
        config = load_config_from_file(
            str(project_path), str(final_config_path),
        )
    except TypeError:
        # Towncrier < 19.9.0
        return load_config_from_file(str(final_config_path))

    if isinstance(config, dict):
        # Towncrier < 22.12.0rc1
        return config

    return _dataclass_to_dict(config)
