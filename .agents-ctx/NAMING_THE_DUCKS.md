# Naming the Ducks

Canonical names for this project, and how to refer to it in
prose. Other files in `.agents-ctx/` (and any generated content)
should say "the project" rather than hardcoding one of these --
reach for a specific name only when the distinction actually
matters (e.g. citing a package, an import, or a repository URL).

## Distribution / PyPI name: `sphinxcontrib-towncrier`

The installable, published name -- recorded in `setup.cfg`'s
`[metadata]` `name`. This is also the preferred way to refer to
the project by name in prose.

## Python import name: `sphinxcontrib.towncrier`

`sphinxcontrib` is a PEP 420 implicit namespace package shared
with other Sphinx extensions -- `src/sphinxcontrib/` has no
`__init__.py`, and must not get one. Sphinx loads the extension
as `sphinxcontrib.towncrier.ext`, which provides the
`towncrier-draft-entries` directive.

## GitHub repository slug: `sphinx-contrib/sphinxcontrib-towncrier`

Use it verbatim when it's actually the repository being
referenced (URLs, `gh` invocations, PR/issue citations) -- not as
a stand-in for the project's name in prose.

## Don't say bare `towncrier`

`towncrier` on its own is the upstream changelog tool whose
unreleased fragments this extension renders, not this project.
The local clone directory may also be called `towncrier`. Say
"Towncrier" for the tool and `sphinxcontrib-towncrier` for this
project.
