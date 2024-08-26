import datetime

import dessinemoi

project = "Dessine-moi"
copyright = f"2021-{datetime.datetime.now().year}, Rayference"
author = "Vincent Leroy"
release = dessinemoi.__version__
version = dessinemoi.__version__

# -- General configuration ---------------------------------------------------

extensions = [
    # Core extensions
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    # Third-party
    "myst_parser",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
]

templates_path = ["_templates"]
source_suffix = [".rst", ".md"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- GitHub quicklinks with 'extlinks' -----------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/extlinks.html

ghbase = "https://github.com"
ghroot = f"{ghbase}/rayference/dessinemoi"
extlinks = {
    "ghissue": (f"{ghroot}/issues/%s", "GH%s"),
    "ghpr": (f"{ghroot}/pull/%s", "PR%s"),
    "ghcommit": (f"{ghroot}/commit/%s", "%.7s"),
    "ghuser": (f"{ghbase}/%s", "@%s"),
}

# -- Extension configuration -------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "attrs": ("https://www.attrs.org/en/stable/", None),
}

autodoc_member_order = "bysource"

# -- Options for HTML output -------------------------------------------------

html_static_path = ["_static"]
html_title = "Dessine-moi"

# Use Furo theme
# https://pradyunsg.me/furo/
html_theme = "furo"
html_theme_options = {
    "navigation_with_keys": True,
}
