"""Towncrier related shims."""

from pathlib import Path
from typing import Union

from towncrier._settings.load import Config  # noqa: WPS436
from towncrier._settings.load import load_config_from_file  # noqa: WPS436
from towncrier._settings.load import (  # noqa: WPS436
    ConfigError as TowncrierConfigError,
)


def get_towncrier_config(
        project_path: Path,
        final_config_path: Union[Path, None],
) -> Config:
    """Return the towncrier config in native format."""
    try:
        return load_config_from_file(str(project_path), str(final_config_path))
    except TowncrierConfigError as config_err:
        raise LookupError(
            'Towncrier was unable to load the configuration from file '
            f'`{final_config_path !s}`: {config_err !s}',
        ) from config_err
