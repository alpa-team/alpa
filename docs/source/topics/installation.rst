Installation
============

The Alpha consists of several components and each of them needs to be set separately:

* To set up the Alpa repository, please see :doc:`repository setup </topics/repository-setup>`
* To set up additional functionality like automatic update of packages, please
  see :doc:`actions </topics/alpa-actions>`

And then there is Alpa CLI. Alpa CLI is a tool that was primarily written for RPM-based
operating systems, but it can be installed on other Linux devices. However, you should
expect that some interesting features like the ``mockbuild`` command will not work.

To install alpa-cli, follow these instructions: https://github.com/alpa-team/alpa#installation

Dependencies
------------

The options for the basic operation of the Alpa CLI are as follows:

* Linux OS
* at least Python 3.9
* other requirements are installed automatically

And for other extra features you need an RPM-based operating system
