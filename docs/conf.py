"""Sphinx configuration."""
project = "hm-python"
author = "Daniel Lee"
copyright = f"2022, {author}"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
]

# To serve html files with python on ubuntu, `python -m http.server <port_num>`
