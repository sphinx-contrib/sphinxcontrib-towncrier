"""Towncrier related shims."""

from contextlib import suppress as suppress_exceptions
from importlib.resources import files as _get_package_resources
from pathlib import Path
from typing import Optional, Set, Union

from towncrier._settings.load import Config  # noqa: WPS436
from towncrier._settings.load import load_config_from_file  # noqa: WPS436
from towncrier._settings.load import (  # noqa: WPS436
    ConfigError as TowncrierConfigError,
)
from towncrier.build import find_fragments


def find_towncrier_fragments(
        base_directory: str,
        towncrier_config: Config,
) -> Set[str]:
    """Look up the change note file paths."""
    with suppress_exceptions(TypeError):
        # Towncrier >= 24.7.0rc1
        _fragments, fragment_filenames = find_fragments(
            base_directory=base_directory,
            config=towncrier_config,
            strict=False,
        )

        return {fname[0] for fname in fragment_filenames}

    # Towncrier < 24.7.0rc1
    try:
        # pylint: disable-next=no-value-for-parameter,unexpected-keyword-arg
        _fragments, fragment_filenames = find_fragments(  # noqa: WPS121
            base_directory=base_directory,
            sections=towncrier_config.sections,
            fragment_directory=towncrier_config.directory,
            frag_type_names=towncrier_config.types,
            orphan_prefix='+',
        )
    except TowncrierConfigError as lookup_err:
        raise LookupError(
            'Towncrier was unable to perform change note lookup: '
            f'{lookup_err !s}',
        ) from lookup_err

    return set(fragment_filenames)


def get_towncrier_config(
        project_path: Path,
        final_config_path: Union[Path, None],
) -> Config:
    """Return the towncrier config in native format."""
    try:
        return load_config_from_file(str(project_path), str(final_config_path))
    except (FileNotFoundError, TowncrierConfigError) as config_load_err:
        raise LookupError(
            'Towncrier was unable to load the configuration from file '
            f'`{final_config_path !s}`: {config_load_err !s}',
        ) from config_load_err


def get_towncrier_template_path(towncrier_config: Config) -> Optional[Path]:
    """Return the Towncrier template file path when it's on disk."""
    if isinstance(towncrier_config.template, str):
        return Path(towncrier_config.template)

    # The template is a `(package, resource)` pair
    package_name, resource_name = towncrier_config.template
    template_path = _get_package_resources(package_name) / resource_name
    # Resources of packages that aren't on disk (like zip-imported ones)
    # cannot be tracked for changes
    return template_path if isinstance(template_path, Path) else None
