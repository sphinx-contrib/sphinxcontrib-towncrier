"""Towncrier related shims."""

from dataclasses import asdict as _dataclass_to_dict
from pathlib import Path
from typing import Any, Dict, Union

from towncrier._settings.load import load_config_from_file  # noqa: WPS436


def get_towncrier_config(
        project_path: Path,
        final_config_path: Union[Path, None],
) -> Dict[str, Any]:  # FIXME: add a better type  # pylint: disable=fixme
    """Return the towncrier config dictionary."""
    config = load_config_from_file(str(project_path), str(final_config_path))

    return _dataclass_to_dict(config)
