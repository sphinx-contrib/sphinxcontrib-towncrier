"""Changelog fragment discovery helpers."""


from functools import lru_cache
from pathlib import Path
from typing import Optional, Set, Tuple

from sphinx.util import logging

from ._towncrier import (  # noqa: WPS436
    find_towncrier_fragments, get_towncrier_config,
    get_towncrier_template_path,
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


def _resolve_config_location(
        working_dir: Optional[str] = None,
        config_path: Optional[str] = None,
) -> Tuple[Path, Path]:
    """Compute the project directory and the Towncrier config paths."""
    project_path = Path.cwd() if working_dir is None else Path(working_dir)

    final_config_path = (
        _resolve_spec_config(project_path, config_path)
        or _find_config_file(project_path)
    )

    return project_path, final_config_path


@lru_cache(maxsize=1, typed=True)
def lookup_towncrier_fragments(
        working_dir: Optional[str] = None,
        config_path: Optional[str] = None,
) -> Set[Path]:
    """Emit RST-formatted Towncrier changelog fragment paths."""
    project_path, final_config_path = _resolve_config_location(
        working_dir, config_path,
    )

    try:
        towncrier_config = get_towncrier_config(
            project_path,
            final_config_path,
        )
    except LookupError as config_lookup_err:
        logger.warning(str(config_lookup_err))
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


@lru_cache(maxsize=1, typed=True)
def lookup_towncrier_config_files(
        working_dir: Optional[str] = None,
        config_path: Optional[str] = None,
) -> Set[Path]:
    """Emit Towncrier config and template file paths."""
    project_path, final_config_path = _resolve_config_location(
        working_dir, config_path,
    )

    if not final_config_path.is_file():
        return set()

    try:
        towncrier_config = get_towncrier_config(
            project_path,
            final_config_path,
        )
    except LookupError:
        # The error is reported by `lookup_towncrier_fragments()` while
        # tracking the broken config lets its fix trigger a rebuild
        return {final_config_path}

    template_path = get_towncrier_template_path(towncrier_config)
    if template_path is None:
        return {final_config_path}

    return {final_config_path, template_path}
