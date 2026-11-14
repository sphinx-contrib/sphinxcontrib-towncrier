"""Changelog fragment discovery helpers."""


import typing as _t
from functools import lru_cache
from pathlib import Path

from sphinx.util import logging

from ._towncrier import (  # noqa: WPS436
    find_towncrier_fragments, get_towncrier_config,
)


logger = logging.getLogger(__name__)


def _resolve_spec_config(
        base: Path, spec_name: _t.Optional[str] = None,
) -> _t.Optional[Path]:
    return None if spec_name is None else base / spec_name


# pylint: disable=fixme
# FIXME: consider consolidating this logic upstream in towncrier
def _find_config_file(base: Path) -> Path:
    """Find the best config file."""
    candidate_names = 'towncrier.toml', 'pyproject.toml'
    candidates = list(map(base.joinpath, candidate_names))
    extant = filter(Path.is_file, candidates)
    return next(extant, candidates[-1])


# pylint: disable=fixme
# FIXME: refactor `lookup_towncrier_fragments` to drop noqas
@lru_cache(maxsize=1, typed=True)  # noqa: WPS210
def lookup_towncrier_fragments(  # noqa: WPS210
        working_dir: _t.Optional[str] = None,
        config_path: _t.Optional[str] = None,
) -> _t.Set[Path]:
    """Emit RST-formatted Towncrier changelog fragment paths."""
    project_path = Path.cwd() if working_dir is None else Path(working_dir)

    final_config_path = (
        _resolve_spec_config(project_path, config_path)
        or _find_config_file(project_path)
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
