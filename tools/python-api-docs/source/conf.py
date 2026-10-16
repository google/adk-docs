# Copyright 2026 Google LLC
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

from datetime import datetime
from google.adk.version import __version__

project = 'Agent Development Kit'
copyright = f'{datetime.now().year}, Google'
author = 'Google'
version = release = __version__
html_title = f'{project} (Python) {release} documentation'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autoclass_content = 'both'

import inspect
import logging

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


extensions = [
    'sphinxcontrib.autodoc_pydantic',
    'sphinxcontrib.googleanalytics',
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
    'sphinx.ext.napoleon',
]

googleanalytics_id = 'G-DKHZS27PHP'

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

autodoc_pydantic_model_show_json = True
autodoc_pydantic_model_show_config_summary = False


# -- Models holding types JSON Schema cannot describe -------------------------
#
# Some ADK models reach, through `google.genai`'s `HttpOptions`, a field that
# can hold a live `aiohttp.ClientSession`. Pydantic validates that by
# `isinstance`, and there is no way to say "an instance of this class" in JSON
# Schema, so generating the schema raises `PydanticInvalidForJsonSchema`.
#
# autodoc_pydantic catches that and retries through a sanitised copy of the
# model, built with `create_model` in its own module's namespace. adk-python
# uses `from __future__ import annotations`, so the copy's annotations are
# strings that no longer resolve there, and the retry dies with
# `PydanticUserError: 'LlmAgentConfig' is not fully defined`. That one is not
# caught, and it fails the whole build - which is how 2.11.0 became
# undocumentable while 2.6.0 built fine.
#
# `show-json-error-strategy` does not help: `add_collapsable_schema` reads
# `schema.sanitized` after the strategy branch, whatever the strategy said.
#
# So the first attempt is made to succeed instead. `is_instance_schema` is
# pydantic's documented override point for exactly this - "unless overridden
# in a subclass, this raises an error" - and the override says what the field
# is rather than pretending it is absent. The alternative was turning off
# `autodoc_pydantic_model_show_json`, which would drop the JSON schema from
# every model page in the reference to accommodate one field.
#
# Patched onto the class rather than passed as a subclass because
# autodoc_pydantic calls `model_json_schema()` with no `schema_generator`,
# taking pydantic's default - which is this class.
from pydantic.json_schema import GenerateJsonSchema as _GenerateJsonSchema


def _is_instance_schema(self, schema):
  """Describe an isinstance-validated field instead of refusing to."""
  cls = schema.get('cls')
  name = getattr(cls, '__qualname__', None) or str(cls)
  module = getattr(cls, '__module__', None)
  full = f'{module}.{name}' if module else name
  return {
      'title': name,
      'description': (
          f'An instance of {full}. This type has no JSON Schema '
          'representation, so only its name is shown here.'
      ),
  }


def _callable_schema(self, schema):
  """As above, for a field holding a callable.

  The same problem and the same answer. Without this, `AntigravityAgent` and
  `RemoteMcpServer` take the retry path below - which happens to survive for
  them today, and is one annotation away from not.
  """
  return {
      'title': 'Callable',
      'description': (
          'A callable. This type has no JSON Schema representation, so only '
          'its kind is shown here.'
      ),
  }


_GenerateJsonSchema.is_instance_schema = _is_instance_schema
_GenerateJsonSchema.callable_schema = _callable_schema


# A backstop under the above, because the retry path is broken in general.
#
# `SchemaInspector.sanitized` tries the model's own schema and, on any
# failure, retries through `create_sanitized_model`. That retry rebuilds the
# model with `create_model` inside autodoc_pydantic's module namespace, which
# cannot work for any package using `from __future__ import annotations`: the
# annotations are strings and no longer resolve there. So the retry does not
# recover, it replaces a specific error with `PydanticUserError` - and that
# one escapes and ends the build.
#
# One model whose schema cannot be rendered should cost that model's schema,
# not the entire reference. Here it costs a stub saying so, and a warning
# naming the model and the real reason, so the underlying problem stays
# visible instead of being papered over.
import sphinx.util.logging as _sphinx_logging
from sphinxcontrib.autodoc_pydantic.inspection import (
    SchemaInspector as _SchemaInspector,
)

_sanitized_schema = _SchemaInspector.sanitized.fget


def _sanitized_or_stub(self):
  try:
    return _sanitized_schema(self)
  except Exception as exc:  # noqa: BLE001 - one model must not fail the build
    name = getattr(self.model, '__name__', 'this model')
    _sphinx_logging.getLogger(__name__).warning(
        f'JSON schema for {name} could not be generated, so the model is '
        f'documented without one: {type(exc).__name__}: {exc}',
        location='autodoc_pydantic',
    )
    return {
        'title': name,
        'description': (
            'A JSON schema could not be generated for this model. The rest '
            'of its documentation below is unaffected.'
        ),
    }


_SchemaInspector.sanitized = property(_sanitized_or_stub)
