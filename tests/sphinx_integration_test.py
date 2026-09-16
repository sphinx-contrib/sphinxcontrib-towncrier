"""End-to-end tests driving real Sphinx builds of the extension."""

from pathlib import Path
from typing import Callable

import pytest

from sphinx.testing.util import SphinxTestApp

from .conftest import (  # noqa: WPS300
    CHANGE_NOTES_DIR_NAME, DEFAULT_FRAGMENT_NAME, DEFAULT_FRAGMENT_TEXT,
    TEXT_ENCODING, SphinxProjectMaker, drop_towncrier_memoization,
)


MakeApp = Callable[..., SphinxTestApp]

CUSTOM_CONFIG_NAME = 'custom-towncrier.toml'

DRAFT_VERSION = '1.2.3'

PARALLEL_READ_PAGE_COUNT = 8

PAGE_TITLE = 'Changelog'

NEW_FRAGMENT_NAME = '2.bugfix.rst'
NEW_FRAGMENT_TEXT = 'Repaired a rusty old thing.'


def _build_html(
        make_app: MakeApp, srcdir: Path, parallel: int = 0,
) -> SphinxTestApp:
    app = make_app('html', srcdir=srcdir, freshenv=False, parallel=parallel)
    app.build()
    return app


def _rendered_index(app: SphinxTestApp) -> str:
    return (Path(app.outdir) / 'index.html').read_text(encoding=TEXT_ENCODING)


def test_draft_entries_rendered_into_html(
        make_app: MakeApp, make_sphinx_project: SphinxProjectMaker,
) -> None:
    """Check that change note contents end up in the built page."""
    app = _build_html(
        make_app, make_sphinx_project(directive_content=DRAFT_VERSION),
    )

    assert DEFAULT_FRAGMENT_TEXT in _rendered_index(app)


def test_directive_argument_sets_version(
        make_app: MakeApp, make_sphinx_project: SphinxProjectMaker,
) -> None:
    """Check that the directive content overrides the draft version."""
    app = _build_html(
        make_app, make_sphinx_project(directive_content=DRAFT_VERSION),
    )

    assert DRAFT_VERSION in _rendered_index(app)


def test_sphinx_release_autoversion(
        make_app: MakeApp, make_sphinx_project: SphinxProjectMaker,
) -> None:
    """Check that ``sphinx-release`` sources the version from Sphinx."""
    srcdir = make_sphinx_project(
        extra_settings=(
            "release = '9.8.7'\n"
            "towncrier_draft_autoversion_mode = 'sphinx-release'"
        ),
    )

    assert '9.8.7' in _rendered_index(_build_html(make_app, srcdir))


@pytest.mark.xfail(
    reason='The `scm-draft` default is not a supported strategy. '
    'Refs: https://github.com/sphinx-contrib/'
    'sphinxcontrib-towncrier/issues/132',
    raises=ValueError,
    strict=True,
)
def test_default_autoversion_mode_is_usable(
        make_app: MakeApp, make_sphinx_project: SphinxProjectMaker,
) -> None:
    """Check that the shipped default needs no directive argument."""
    _build_html(make_app, make_sphinx_project())


def test_empty_changelog_omitted(
        make_app: MakeApp, make_sphinx_project: SphinxProjectMaker,
) -> None:
    """Check that an empty draft renders nothing when not included."""
    srcdir = make_sphinx_project(
        fragments={},
        extra_settings='towncrier_draft_include_empty = False',
        directive_content=DRAFT_VERSION,
    )
    rendered_page = _rendered_index(_build_html(make_app, srcdir))

    assert PAGE_TITLE in rendered_page  # the page itself did get built
    assert 'No significant changes' not in rendered_page


def test_empty_changelog_included(
        make_app: MakeApp, make_sphinx_project: SphinxProjectMaker,
) -> None:
    """Check that an empty draft is rendered when included."""
    srcdir = make_sphinx_project(fragments={}, directive_content=DRAFT_VERSION)
    rendered_page = _rendered_index(_build_html(make_app, srcdir))

    assert PAGE_TITLE in rendered_page
    assert 'No significant changes' in rendered_page


def test_custom_config_path_honored(
        make_app: MakeApp, make_sphinx_project: SphinxProjectMaker,
) -> None:
    """Check that an explicitly pointed-at config is picked up."""
    srcdir = make_sphinx_project(
        extra_settings=(
            f'towncrier_draft_config_path = {CUSTOM_CONFIG_NAME!r}'
        ),
        directive_content=DRAFT_VERSION,
        towncrier_config_name=CUSTOM_CONFIG_NAME,
    )

    assert DEFAULT_FRAGMENT_TEXT in _rendered_index(
        _build_html(make_app, srcdir),
    )


def test_missing_towncrier_config_reports_errors(
        make_app: MakeApp, make_sphinx_project: SphinxProjectMaker,
) -> None:
    """Check that an absent Towncrier config surfaces diagnostics."""
    srcdir = make_sphinx_project(
        towncrier_config=None, directive_content=DRAFT_VERSION,
    )
    app = _build_html(make_app, srcdir)
    build_warnings = app.warning.getvalue()

    assert 'unable to load the configuration from file' in build_warnings
    assert 'Command exited unexpectedly' in build_warnings


def test_second_directive_argument_rejected(
        make_app: MakeApp, make_sphinx_project: SphinxProjectMaker,
) -> None:
    """Check that a multi-line directive body is an error."""
    srcdir = make_sphinx_project(
        directive_content=f'{DRAFT_VERSION}\n   4.5.6',
    )
    app = _build_html(make_app, srcdir)

    assert 'only one argument permitted' in app.warning.getvalue()


def test_added_fragment_rebuilds_doc(
        make_app: MakeApp, make_sphinx_project: SphinxProjectMaker,
) -> None:
    """Check that a new change note forces a page rebuild."""
    srcdir = make_sphinx_project(directive_content=DRAFT_VERSION)
    _build_html(make_app, srcdir)

    change_notes_dir = srcdir.parent / CHANGE_NOTES_DIR_NAME
    (change_notes_dir / NEW_FRAGMENT_NAME).write_text(
        f'{NEW_FRAGMENT_TEXT}\n', encoding=TEXT_ENCODING,
    )
    drop_towncrier_memoization()

    assert NEW_FRAGMENT_TEXT in _rendered_index(_build_html(make_app, srcdir))


def test_removed_fragment_rebuilds_doc(
        make_app: MakeApp, make_sphinx_project: SphinxProjectMaker,
) -> None:
    """Check that a deleted change note forces a page rebuild."""
    srcdir = make_sphinx_project(
        fragments={
            DEFAULT_FRAGMENT_NAME: DEFAULT_FRAGMENT_TEXT,
            NEW_FRAGMENT_NAME: NEW_FRAGMENT_TEXT,
        },
        directive_content=DRAFT_VERSION,
    )
    _build_html(make_app, srcdir)

    (srcdir.parent / CHANGE_NOTES_DIR_NAME / NEW_FRAGMENT_NAME).unlink()
    drop_towncrier_memoization()

    assert NEW_FRAGMENT_TEXT not in _rendered_index(
        _build_html(make_app, srcdir),
    )


def test_parallel_read_merges_fragment_deps(
        make_app: MakeApp, make_sphinx_project: SphinxProjectMaker,
) -> None:
    """Check that parallel reads merge the collected fragment deps.

    Sphinx only parallelizes reading when there are more than five
    documents, hence the filler pages.
    """
    srcdir = make_sphinx_project(directive_content=DRAFT_VERSION)
    index_rst = (srcdir / 'index.rst').read_text(encoding=TEXT_ENCODING)
    for page_number in range(PARALLEL_READ_PAGE_COUNT):
        (srcdir / f'page{page_number}.rst').write_text(
            index_rst, encoding=TEXT_ENCODING,
        )

    app = _build_html(make_app, srcdir, parallel=2)
    collected_docs = (
        app.env.towncrier_fragment_docs  # type: ignore[attr-defined]
    )

    assert DEFAULT_FRAGMENT_TEXT in _rendered_index(app)
    assert len(collected_docs) == PARALLEL_READ_PAGE_COUNT + 1
