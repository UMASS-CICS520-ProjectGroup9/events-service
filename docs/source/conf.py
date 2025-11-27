# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'events-service'
copyright = '2025, Nalongsone Danddank'
author = 'Nalongsone Danddank'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
import sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, BASE_DIR)  # repo root
sys.path.insert(0, os.path.join(BASE_DIR, "eventsService"))  # Django project package

# Initialize Django so autodoc works for project modules.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventsService.settings')
try:
    import django
    django.setup()
except Exception as exc:  # avoid hard fail to get clearer Sphinx error messages
    print(f"Warning: Django setup failed: {exc}")

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
