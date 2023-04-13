.. _`alpa_cli_manual_page`:

CLI setup
=========

For some commands, Alpa needs to communicate directly with the GitHub API and therefore needs
to specify your GitHub token. To know which commands needs to use GitHub token, please see
:doc:`alpa-cli commands </autodoc/alpa.cli>` section.


Set up GitHub token for Alpa
----------------------------

To set up a GitHub token, follow `GitHub documentation`_. Give this token only the rights it really
needs (read/write access to the repository). You can provide this token to alpa-cli as an
environment variable::

    $  export ALPA_GH_API_TOKEN=your_gh_token

.. caution::
  Make sure you leave a space before the command so that this command is not stored in the history.

Or you can specify the tokens in `local configuration file`_.

.. _`GitHub documentation`: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token


.. _`local configuration file`:

Configuration file
------------------

If you don't want to give access to all your repositories through the GitHub API token,
GitHub offers `Fine-grained personal access tokens`_. With these you can specify each token
for each repository without worrying that alpa-cli has access somewhere it shouldn't.

You can store multiple GitHub tokens in alpa-cli's configuration file located in
``~/.config/alpa.yaml`` or in ``/etc/alpa.yaml``. The user configuration file takes
precedence.

.. caution::
  This is not the same configuration file as in ``<git_root>/.alpa.yaml``!

The configuration file has list of GitHub token keys for each repository.

Example:

.. code-block:: yaml

    ---
    api_keys:
      - repo:
          name: my-repo-name
          key: my-secret-gh-token-to-my-repo-name
      - repo:
          name: another-repo
          key: my-secret-gh-token-to-another-repo
      - repo:
          name: yet-another-repo
          key: my-secret-gh-token-to-yet-another-repo

For each repo you specify ``name`` (your repository name on GitHub) and a corresponding
GitHub token key to it. Alpa-cli will use only this key for communication with this
repository.

.. _`Fine-grained personal access tokens`: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token#fine-grained-personal-access-tokens
