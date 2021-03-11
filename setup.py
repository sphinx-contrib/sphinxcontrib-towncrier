#! /usr/bin/env python3

# NOTE: THIS FILE IS IMMUTABLE AND SHOULD REMAIN UNCHANGED UNLESS THERE ARE
# NOTE: SERIOUS REASONS TO EDIT IT. THIS IS ENFORCED BY THE PRE-COMMIT TOOL.

"""The distribution package setuptools installer for sphinxcontrib-towncrier.

The presence of this file ensures the support of pip editable mode
*with setuptools only*.

It is also required for `tox --devenv some-env-folder` command to work
because it does `pip install -e .` under the hood.
"""
from setuptools import setup


# pylint: disable=expression-not-assigned
__name__ == '__main__' and setup()  # noqa: WPS428
