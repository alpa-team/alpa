Overview
========

Alpa is basically a software repository which stores RPM packages in GitHub repository. You can make
as many RPMs for different operating systems or targets as they are supported by Copr (to know for
what targets are supported by Copr, see :ref:`copr_targets`). To create an RPM package, you only
need to create a spec file, correctly specify the upstream source in it from which the source
will be downloaded and specify some metadata like your GitHub username in case somebody want to
contact you.


What is Alpa's use-case
-----------------------

The main advantage of Alpa is that you can pack a lot of RPM packages that you don't develop
directly and put them into one big repository and maintain them from one place. So if you decide
to set up a repository for a bunch of e.g. bioinformatics or astronomy programs with a couple
of maintainers on your team, but you don't want to maintain each package separately in a separate
repository, Alpa is the right tool for you since it allows you to manage everything from one place.


Components
----------

Alpa consists of several independent components, which together behave as a whole providing the
functionality of a software repository.

CLI
~~~

A key component (besides the correct configuration of the repository itself) is the Alpa
CLI, which helps maintainers to communicate correctly with the repository.
This command line interface allows package maintainers to manage a package, make
modifications to it, and then push those modifications to the repository. For more, see
:ref:`alpa_cli_manual_page`

Actions
~~~~~~~

You can also extend the basic functionality of the repository with two tools that are designed
as GitHub Actions for easy deployment to the repository. These are for deleting packages and
adding new packages privately without commit permissions to the repository. The second
functionality is the automatic detection of a new version of an upstream program and
its subsequent automatic update.

* To know more about deleting/adding packages, see :ref:`manage_package`
* To know more about automatic updates, see :ref:`automatic_updates`


.. _`copr_targets`:

Copr targets
------------

Copr supports many targets for which you can create RPM packages. To see all possible
targets, please install ``copr-cli`` and then run this command::

    $ copr list-chroots
    amazonlinux-2023-aarch64
    amazonlinux-2023-x86_64
    centos-stream+epel-next-8-aarch64
    centos-stream+epel-next-8-ppc64le
    centos-stream+epel-next-8-x86_64
    centos-stream+epel-next-9-aarch64
    ...
