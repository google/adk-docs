# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Agent Development Kit'
copyright = '2025, Google'
author = 'Google'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autoclass_content = 'both'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']

import html
import inspect
import inspect
import logging  # Use logging for better output
import os
import sys
import pydantic


def skip_pydantic_init(app, what, name, obj, options, lines):
  logging.info(
      f'Processing: what={what}, name={name}, obj={obj}, type(obj)={type(obj)}'
  )

  if what == 'pydantic_model':
    try:
      mro = inspect.getmro(obj)
      logging.info(f'  MRO: {mro}')
      if inspect.isclass(mro[0]) and issubclass(mro[0], pydantic.BaseModel):
        # Check if the *first class in the MRO* has a default docstring
        # (This is a heuristic, but it's likely to be correct for BaseModel's init)
        if lines and lines[0].startswith('Create a new model by parsing'):
          logging.info("  Suppressing BaseModel's __init__ docstring")
          lines.clear()
          lines.append('')
    except TypeError:
      logging.info('  obj is not a class-like object (pydantic_model)')
  elif what == 'method' and name == '__init__':
    # This is likely not necessary, but keep it for robustness
    try:
      mro = inspect.getmro(obj)
      logging.info(f'  MRO: {mro}')
      if inspect.isclass(mro[0]) and issubclass(mro[0], pydantic.BaseModel):
        logging.info('  Suppressing __init__ docstring (method)')
        lines.clear()
        lines.append('')
    except TypeError:
      logging.info('  obj is not a class-like object (method)')


def setup(app):
  app.connect('autodoc-process-docstring', skip_pydantic_init)
  logging.basicConfig(level=logging.INFO)


sys.path.insert(0, os.path.abspath('.'))  # Add current directory to path
sys.path.insert(0, os.path.abspath('../google'))

extensions = [
    'sphinxcontrib.autodoc_pydantic',
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
    'sphinx.ext.napoleon',
]
html_theme = 'furo'

TEXT_FONTS = (
    '"Google Sans Text", Roboto, "Helvetica Neue", Helvetica, Arial, sans-serif'
)
CODE_FONTS = 'Roboto Mono, "Helvetica Neue Mono", monospace'
FONT_COLOR_FOR_LIGHT_THEME = 'black'
FONT_COLOR_FOR_DARK_THEME = 'white'

html_theme_options = {
    'light_css_variables': {
        'font-stack': TEXT_FONTS,
        'font-stack--monospace': CODE_FONTS,
        'font-stack--headings': TEXT_FONTS,
        'color-brand-primary': FONT_COLOR_FOR_LIGHT_THEME,
        'color-brand-content': FONT_COLOR_FOR_LIGHT_THEME,
    },
    'dark_css_variables': {
        'font-stack': TEXT_FONTS,
        'font-stack--monospace': CODE_FONTS,
        'font-stack--headings': TEXT_FONTS,
        'color-brand-primary': FONT_COLOR_FOR_DARK_THEME,
        'color-brand-content': FONT_COLOR_FOR_DARK_THEME,
    },
}

# These folders are copied to the documentation's HTML output
html_static_path = ['_static']

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    'css/custom.css',
]

autodoc_pydantic_model_show_json = True
autodoc_pydantic_model_show_config_summary = False
