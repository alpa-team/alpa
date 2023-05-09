Configuration file
==================

Alpa repository on GitHub has a configuration file. The following names are accepted::

    * .alpa.yaml
    * .alpa.yml
    * alpa.yaml
    * alpa.yml

The ``yaml`` file has these attributres:

``repo_type``
  ``branch`` or ``subdirectory``: Do not change this field since this is under a development.

``copr_owner``
  ``string``: The owner of Copr repository.

``copr_repo``
  ``string``: The name of Copr repository under right Copr owner.

[Optional] ``allow_foreign_contributing``
  ``boolean``:  Allow foreign contributors to contribute and create packages in your repository.

These two adds chroots for building on global level for all packages:

[Optional] ``targets``
  ``list of strings``:  This field is a list of :ref:`copr_targets`

[Optional] ``arch``
  ``list of strings``:  Architectures you want to build for.
