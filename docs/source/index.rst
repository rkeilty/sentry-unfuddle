.. sentry-unfuddle documentation master file, created by
   sphinx-quickstart on Mon Sep 10 15:06:37 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to sentry-unfuddle's documentation
==========================================


Configuration Overview
----------------------

Go to your project's configuration page (Projects -> [Project]) and select the
Unfuddle tab. Enter the Unfuddle credentials and Project configuration and save changes.
Filling out the form is a two step process (one to fill in data, one to select
project).

Configuration Tips
------------------

 - Sentry >= 7.0.0 is required.

 - You should use `https://<instanceurl>` for the configuration since the plugin
   uses basic auth with the Unfuddle API to authenticate requests.

 - You need to configure the plugin for each Sentry project, and you have the
   ability to assign a default Unfuddle project for each Sentry project.


Change Log
----------

There have been a few changes recently that depend on the version of sentry
that is installed alongside the plugin, so I'm keeping track of changes for
versions of the plugins (along with which version of sentry they actually
support).

1.0.0
#####

 - Updated documentation
 - Made version 1.0.0, as this has been running successfully in several production environments.

0.11.0
######

 - Initial port of [sentry-jira](https://github.com/getsentry/sentry-jira) to [sentry-unfuddle](https://github.com/rkeilty/sentry-unfuddle)

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
