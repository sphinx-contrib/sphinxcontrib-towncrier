"""Changelog fragment discovery helpers."""


from functools import lru_cache
from pathlib import Path
from typing import Optional, Set, Tuple

from sphinx.util import logging

from ._towncrier import (  # noqa: WPS436
    Config, find_towncrier_fragments, get_towncrier_config,
)


logger = logging.getLogger(__name__)


def _resolve_spec_config(
        base: Path, spec_name: Optional[str] = None,
) -> Optional[Path]:
    return base / spec_name if spec_name is not None else None


# pylint: disable=fixme
# FIXME: consider consolidating this logic upstream in towncrier
def _find_config_file(base: Path) -> Path:
    """Find the best config file."""
    candidate_names = 'towncrier.toml', 'pyproject.toml'
    candidates = list(map(base.joinpath, candidate_names))
    extant = filter(Path.is_file, candidates)
    return next(extant, candidates[-1])


def _resolve_project_path(working_dir: Optional[str] = None) -> Path:
    return Path.cwd() if working_dir is None else Path(working_dir)


def resolve_towncrier_config_path(
        working_dir: Optional[str] = None,
        config_path: Optional[str] = None,
) -> Path:
    """Compute the Towncrier config file path to be loaded."""
    project_path = _resolve_project_path(working_dir)
    return (
        _resolve_spec_config(project_path, config_path)
        or _find_config_file(project_path)
    )


def _load_towncrier_config(
        working_dir: Optional[str] = None,
        config_path: Optional[str] = None,
) -> Optional[Config]:
    """Load the Towncrier config, warning when it's unavailable."""
    try:
        return get_towncrier_config(
            _resolve_project_path(working_dir),
            resolve_towncrier_config_path(working_dir, config_path),
        )
    except LookupError as config_lookup_err:
        logger.warning(str(config_lookup_err))
        return None


@lru_cache(maxsize=1, typed=True)
def lookup_towncrier_fragment_categories(
        working_dir: Optional[str] = None,
        config_path: Optional[str] = None,
) -> Tuple[Tuple[str, str], ...]:
    """Emit the configured change note categories and their titles.

    The first element of each pair is the category name that the change
    note file names are suffixed with. The second one is the
    human-readable section title Towncrier renders it under.
    """
    towncrier_config = _load_towncrier_config(working_dir, config_path)
    if towncrier_config is None:
        return ()

    return tuple(
        (category, category_spec['name'] or category)
        for category, category_spec in towncrier_config.types.items()
    )


@lru_cache(maxsize=1, typed=True)
def lookup_towncrier_fragments(
        working_dir: Optional[str] = None,
        config_path: Optional[str] = None,
) -> Set[Path]:
    """Emit RST-formatted Towncrier changelog fragment paths."""
    project_path = _resolve_project_path(working_dir)

    towncrier_config = _load_towncrier_config(working_dir, config_path)
    if towncrier_config is None:
        return set()

    try:
        fragment_filenames = find_towncrier_fragments(
            str(project_path),
            towncrier_config,
        )
    except LookupError as change_notes_lookup_err:
        logger.warning(str(change_notes_lookup_err))
        return set()

    return set(map(Path, fragment_filenames))
