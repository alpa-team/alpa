Welcome to Alpa's documentation!
================================

.. toctree::
    :maxdepth: 2
    :hidden:
    :caption: Getting started

    /topics/overview
    /topics/installation

.. toctree::
    :maxdepth: 2
    :hidden:
    :caption: Creating your own Alpa repository

    /topics/repository-setup
    /topics/repo-config-file
    /topics/pre-commit-hooks
    /topics/alpa-actions

.. toctree::
    :maxdepth: 2
    :hidden:
    :caption: Creating a new package

    /topics/package-creation-tutorial
    /topics/package-data
    /topics/release-monitoring
    /topics/first-package

.. toctree::
    :maxdepth: 2
    :hidden:
    :caption: Command line interface

    /topics/alpa-cli-manual
    /autodoc/alpa.cli

.. TODO: explain what is going on for advanced users

.. toctree::
    :maxdepth: 2
    :hidden:
    :caption: Explanation

.. toctree::
    :maxdepth: 2
    :hidden:
    :caption: Contributing

    /topics/contributing


Alpa is a set of tools that together form a whole capable of creating
a software repository of RPM packages located in GitHub. To add a new
package, all you need is a `spec file`_, an URL where the upstream software
is developed and some git basics. The system will take care of the rest.


.. _`spec file`: https://docs.fedoraproject.org/en-US/packaging-guidelines/#_spec_files

Getting started
---------------

:doc:`Overview </topics/overview>`
:doc:`Installation </topics/installation>`


Create your own Alpa repository
-------------------------------

:doc:`Alpa repository setup </topics/repository-setup>`

Add more functionality to your Alpa repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:doc:`Alpa repository configuration file </topics/repo-config-file>`
:doc:`pre-commit hooks Alpa offers </topics/pre-commit-hooks>`
:doc:`GitHub Actions Alpa offers </topics/alpa-actions>`


Create new package to Alpa repo
-------------------------------

:doc:`Tutorial how to create package </topics/package-creation-tutorial>`
:doc:`Data needed to create package </topics/package-data>`
:doc:`Release monitoring </topics/release-monitoring>`
:doc:`Creating package for the first time </topics/first-package>`
