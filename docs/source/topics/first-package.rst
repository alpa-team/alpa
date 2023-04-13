Creating package for the first time
===================================

If this is the first time you have created a package in the repository, you will end up
with an error because you need to enable Packit rights to your Copr repository.

.. _`error in pull requests`:

Error in Pull Request
---------------------

In case of Pull Requests the GitHub Check will fail and Packit bot will drop this comment:

.. image:: /images/packit-builder-permission-PR.png

How to solve this:

* Go to your ``<project-name>-pull-requests`` repository in Copr
* Go to ``Settings`` -> ``Permissions`` and set up the permission for packit to
  ``approved`` like this:

.. image:: /images/packit-builder-permission-PR-Copr.png

* And click ``Update``
* Go to the failed PR and drop down a ``/packit build`` comment, which will re-trigger
  the build again


.. _`error in package branch`:

Error in package branch
-----------------------

In case of merging the PR for the first time, the GitHub Run in package branch will fail:

.. image:: /images/branch-run-fail.png

How to solve this:

* Go to your ``<project-name>`` repository in Copr
* Go to ``Settings`` -> ``Permissions`` and set up the permission for packit to
  ``approved`` like this:

.. image:: /images/packit-builder-permission-Copr.png

* And click ``Update``
* Go to the GitHub repository
* Go to the desired package branch
* Click on the red cross next to commit sha
* Click ``Details`` in the pop-up window
* Re-run on each failed check.
