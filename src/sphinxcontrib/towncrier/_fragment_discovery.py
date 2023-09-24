"""Changelog fragment discovery helpers."""


from functools import lru_cache
from pathlib import Path
from typing import Optional, Set

from sphinx.util import logging


try:
    # pylint: disable=no-name-in-module
    from towncrier.build import find_fragments  # noqa: WPS433
except ImportError:
    # pylint: disable=import-self,no-name-in-module
    from towncrier import (  # type: ignore[attr-defined] # noqa: WPS433,WPS440
        find_fragments,
    )

from ._towncrier import get_towncrier_config  # noqa: WPS436


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


# pylint: disable=fixme
# FIXME: refactor `lookup_towncrier_fragments` to drop noqas
@lru_cache(maxsize=1, typed=True)  # noqa: WPS210
def lookup_towncrier_fragments(  # noqa: WPS210
        working_dir: Optional[str] = None,
        config_path: Optional[str] = None,
) -> Set[Path]:
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
    except KeyError as key_err:
        # NOTE: The error is missing key 'towncrier' or similar
        logger.warning(
            f'Missing key {key_err!s} in file {final_config_path!s}',
        )
        return set()

    fragment_directory: Optional[str] = 'newsfragments'
    try:
        fragment_base_directory = project_path / towncrier_config['directory']
    except KeyError:
        assert fragment_directory is not None
        fragment_base_directory = project_path / fragment_directory
    else:
        fragment_directory = None

    _fragments, fragment_filenames = find_fragments(
        str(fragment_base_directory),
        towncrier_config['sections'],
        fragment_directory,
        towncrier_config['types'],
    )
    return set(fragment_filenames)
