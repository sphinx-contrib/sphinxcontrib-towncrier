"""Sphinx extension for injecting an unreleased changelog into docs.

This is an importable package containing the whole project. The Sphinx
extension entry point is declared in the :file:`ext` submodule.

To use this extension, add the following to your :file:`conf.py`:

.. code-block:: python

    extensions = ['sphinxcontrib.towncrier.ext']

"""

from .ext import __version__, setup
