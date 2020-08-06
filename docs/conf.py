from datetime import date, datetime

import sphinx_rtd_theme

from sphinxcontrib.towncrier import __version__

company = "sphinxcontrib"
name = "sphinxcontrib-towncrier"
version = ".".join(__version__.split(".")[:2])
release = __version__
copyright = f"2020-{date.today().year}, {company}"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.extlinks",
]

templates_path = []
unused_docs = []
source_suffix = ".rst"
exclude_patterns = ["_build", "changelog/*"]

master_doc = "index"
pygments_style = "default"
always_document_param_types = True
project = name
today_fmt = "%B %d, %Y"

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {
    "canonical_url": "",
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 6,
    "includehidden": True,
}
html_static_path = ["_static"]
html_last_updated_fmt = datetime.now().isoformat()
htmlhelp_basename = "Pastedoc"
autosectionlabel_prefix_document = True

extlinks = {
    "user": ("https://github.com/%s", "@"),
}


def setup(app):
    app.add_css_file("custom.css")
