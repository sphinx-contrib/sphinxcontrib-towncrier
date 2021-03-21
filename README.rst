sphinxcontrib-towncrier
=======================

An RST directive for injecting a Towncrier-generated changelog draft containing fragments for the unreleased (next) project version


How to use this?
----------------

.. code-block:: shell-session

    $ pip install sphinxcontrib-towncrier

.. code-block:: python

    extensions = ['sphinxcontrib.towncrier']

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
