GitHub Actions
==============

Alpa provides two independent GitHub Actions that extend the functionality of the Alpa
repository. If you want to use these features, just configure the ``.github`` directory
in the repository and set up the correct ``Secrets``.

.. danger::
  For sensitive data, such as a GitHub token or similar otherwise sensitive data, use
  `GitHub Secrets`_!

.. _GitHub Secrets: https://docs.github.com/en/rest/actions/secrets?apiVersion=2022-11-28

.. _`manage_package`:

Manage package requests for Alpa repository
-------------------------------------------

This GitHub Action available `here`_ allows you to delete packages from the GitHub repository
and also at the same time from the Copr repository and allows contributors who don't have commit
access to your repository to create new packages (but you have to explicitly enable this option
in the ``.alpa.yaml`` configuration file under the ``allow_foreign_contributing`` field)

To set up this action properly, please follow instruction documented on
`Manage Alpa Package marketplace`_

.. _`here`: https://github.com/alpa-team/manage-package
.. _Manage Alpa Package marketplace: https://github.com/marketplace/actions/manage-alpa-package

.. _`automatic_updates`:

Automatically update packages
-----------------------------

This GitHub Action available `from here`_ is used to automatically update packages in the
repository. In order for a package to update itself, you must fill in the ``autoupdate`` field
in the ``metadata.yaml`` configuration file of the package.

Some useful links how to set up this action:

* For the correct way to fill in the ``autoupdate`` field, see :ref:`autoupdate`.
* To set up this action properly in your Alpa repository, please follow instruction
  documented on `Autoupdate Alpa repository marketplace`_

.. _from here: https://github.com/alpa-team/autoupdate-alpa-repo
.. _Autoupdate Alpa repository marketplace: https://github.com/marketplace/actions/autoupdate-alpa-repository
