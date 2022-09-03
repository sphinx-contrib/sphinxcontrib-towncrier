.. image:: https://img.shields.io/pypi/v/sphinxcontrib-towncrier.svg?logo=Python&logoColor=white
   :target: https://pypi.org/project/sphinxcontrib-towncrier
   :alt: sphinxcontrib-towncrier @ PyPI

.. image:: https://github.com/sphinx-contrib/sphinxcontrib-towncrier/actions/workflows/tox-tests.yaml/badge.svg?event=push
   :target: https://github.com/sphinx-contrib/sphinxcontrib-towncrier/actions/workflows/tox-tests.yaml
   :alt: GitHub Actions CI/CD build status — Python package

.. image:: https://codecov.io/gh/sphinx-contrib/sphinxcontrib-towncrier/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/sphinx-contrib/sphinxcontrib-towncrier
   :alt: sphinxcontrib-towncrier coverage charts @ Covecov.io

.. DO-NOT-REMOVE-docs-badges-END

.. image:: https://img.shields.io/readthedocs/sphinxcontrib-towncrier/latest.svg?logo=Read%20The%20Docs&logoColor=white
   :target: https://sphinxcontrib-towncrier.rtfd.io/en/latest/?badge=latest
   :alt: Documentation Status @ RTD

sphinxcontrib-towncrier
=======================

.. DO-NOT-REMOVE-docs-intro-START

An RST directive for injecting a Towncrier-generated changelog draft
containing fragments for the unreleased (next) project version.


How to use this?
----------------

.. code-block:: shell-session

    $ pip install sphinxcontrib-towncrier

.. code-block:: python

    extensions = ['sphinxcontrib.towncrier.ext']

    # Options: draft/sphinx-version/sphinx-release
    towncrier_draft_autoversion_mode = 'draft'
    towncrier_draft_include_empty = True
    towncrier_draft_working_directory = PROJECT_ROOT_DIR
    # Not yet supported:
    # towncrier_draft_config_path = 'pyproject.toml'  # relative to cwd

Make sure to point to the dir with ``pyproject.toml`` and pre-configure
towncrier itself in the config.

If everything above is  set up correctly, you should be able to add

.. code-block:: rst

    .. towncrier-draft-entries::

to your documents, like ``changelog.rst``. With no argument, the version
title will be generated using the strategy set up in the
``towncrier_draft_autoversion_mode`` setting.

If you want to be in control, override it with an argument you like:

.. code-block:: rst

    .. towncrier-draft-entries:: |release| [UNRELEASED DRAFT]

Native RST substitutions in the argument work, just make sure to declare
any non-default ones via ``rst_epilog`` or at the end of the document
where the ``towncrier-draft-entries`` directive is being used.


Does anybody actually use this?
-------------------------------

So far we know about two projects using ``sphinxcontrib-towncrier`` —
ansible/pylibssh and pypa/pip. Also, this Sphinx extension is inspired
by and somewhat based on the ideas used in pytest-dev/pytest and
tox-dev/tox. We believe that these projects are full of wonderful tricks
that you may want to explore regardless of whether you'll use our
project.
