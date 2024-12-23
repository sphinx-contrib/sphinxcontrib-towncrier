"""Towncrier related shims."""

from pathlib import Path
from typing import Union

from towncrier._settings.load import (  # noqa: WPS436
    Config, load_config_from_file,
)


def get_towncrier_config(
        project_path: Path,
        final_config_path: Union[Path, None],
) -> Config:
    """Return the towncrier config in native format."""
    return load_config_from_file(str(project_path), str(final_config_path))
