"""Changelog fragment discovery helpers."""


from functools import lru_cache
from pathlib import Path
from typing import Optional, Set

from sphinx.util import logging
# pylint: disable-next=no-name-in-module
from towncrier.build import find_fragments  # noqa: WPS433

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
    except LookupError as lookup_err:
        logger.warning(str(lookup_err))
        return set()

    fragment_directory: Optional[str] = 'newsfragments'
    try:
        fragment_base_directory = project_path / towncrier_config.directory
    except TypeError:
        assert fragment_directory is not None
        fragment_base_directory = project_path / fragment_directory
    else:
        fragment_directory = None

    try:
        # Towncrier < 24.7.0rc1
        # pylint: disable-next=no-value-for-parameter,unexpected-keyword-arg
        _fragments, fragment_filenames = find_fragments(
            base_directory=str(fragment_base_directory),
            sections=towncrier_config.sections,
            fragment_directory=fragment_directory,
            frag_type_names=towncrier_config.types,
            orphan_prefix='+',
        )
    except TypeError:
        # Towncrier >= 24.7.0rc1
        _fragments, fragment_filenames = find_fragments(  # noqa: WPS121
            base_directory=str(fragment_base_directory),
            config=towncrier_config,
            strict=False,
        )

        return {Path(fname[0]) for fname in fragment_filenames}

    return set(fragment_filenames)
