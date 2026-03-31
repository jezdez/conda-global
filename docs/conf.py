"""Sphinx configuration for conda-global docs."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = html_title = "conda-global"
copyright = "2026, conda community"
author = "Jannis Leidel"

extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_design",
]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "tasklist",
]

html_theme = "conda_sphinx_theme"

html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/jezdez/conda-global",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/conda-global/",
            "icon": "fa-brands fa-python",
            "type": "fontawesome",
        },
    ],
}

html_context = {
    "github_user": "jezdez",
    "github_repo": "conda-global",
    "github_version": "main",
    "doc_path": "docs",
}

html_static_path = ["_static"]
html_css_files = ["css/custom.css"]

html_baseurl = "https://jezdez.github.io/conda-global/"

exclude_patterns = ["_build"]
