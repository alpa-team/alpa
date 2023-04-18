Release monitoring
==================

Release monitoring, as the name suggests, monitors software on various sites such as
GitHub, PyPI, Sourcefoge, etc. Alpa uses the release monitoring API to find out the
current version of a package and if it does not match the current version of the
package in the GitHub Alpa repository, it will perform an update.


Use Anitya for your package
---------------------------

If you want Alpa to automatically update your package, you need to see if Anitya has
a record of your package. Simply use the search box at https://release-monitoring.org.
Select the desired package and fill in its name in :ref:`metadata.yaml` in the ``autoupdate``
field under ``upstream_pkg_name``. Do the same for ``backend``

.. tip::
  Anitya supports a lot of backends. You can view all of them on their `docs page`_

.. _`docs page`: https://release-monitoring.org/static/docs/user-guide.html#backends


Create new package monitoring in Anitya
---------------------------------------

In case Anitya is not tracking the package you requested, log in with your Fedora
account at https://release-monitoring.org/login. After logging in, you will see an
``add project`` box on the top left and fill in the necessary information, then
click ``Submit``. Anitya has this process well documented on
https://release-monitoring.org/static/docs/user-guide.html#creating-new-project.

.. warning::
  When adding a project, make sure ``Homepage`` uses the same source as you specified
  in ``Source0`` in spec file. Because if Anitya found a new version on GitHub, for
  example, but you put a PyPI into ``Source0`` that the upstream hasn't released
  yet, the autoupdate will fail.
