sentry-unfuddle
===============

A flexible extension for Sentry which allows you to create issues in
Unfuddle based on sentry events. It is based off the implementation for
`sentry-jira <https://github.com/getsentry/sentry-jira>`__.

Currently it works with Sentry 7 and 8.

Installation
============

The sentry-unfuddle module is `published on the Python Package
Index <https://pypi.python.org/pypi/sentry-unfuddle>`__, so you can
install it using ``pip`` or ``easy_install``.

::

    pip install sentry-unfuddle

Or:

::

    easy_install sentry-unfuddle

This is a server plugin, so it needs to be installed into the same
Python environment you are running your Sentry instance from.

Configuration
=============

Go to your project's configuration page (``Projects -> [Project]``) and
select the Unfuddle tab. Enter the Unfuddle credentials and Project
configuration and save changes. Filling out the form is a two step
process (one to fill in your instance details and credentials, one to
select the project to link to).

The user you add on the configuration screen is the one used to process
API requests, so ensure that user has ``Account Administrator`` or at
the very least ``Project Administrator`` privileges.

Usage
=====

Once configured, users will see a link to "Create Unfuddle issue" on the
event page. Clicking on that brings you to a page in which you can
select a user to assign the issue to, select an upcoming milestone, and
select a priority (defaults to ``High``.) The "title" and "description"
fields are prepopulated with the data from the event.

The plugin will try to be smart when creating an issue on Unfuddle. If
it finds a user that matches the currently logged in Sentry user, it
will make that user the reporter of the ticket (if no match, defaults to
the user from the configuration page.)

License
=======

``sentry-unfuddle`` is licensed under the terms of the 3-clause BSD
license.

Contributing
============

All contributions are welcome, including but not limited to:

-  Documentation fixes / updates
-  New features (requests as well as implementations)
-  Bug fixes (see issues list)

If you encounter any errors in the code, please file an issue on github:
https://github.com/rkeilty/sentry-unfuddle/issues.

Author
======

-  Author: Rick Keilty
-  Email: rkeilty@gmail.com
-  Repository: http://github.com/rkeilty/sentry-unfuddle

Version
=======

-  Version: 1.0.1
-  Release Date: 2016-01-23

Revision History
================

Version 1.0.1
-------------

-  Release Date: 2016-01-23
-  Changes:

   -  Updated documentation
   -  Confirmed working with Sentry 8.0.x

Version 1.0.0
-------------

-  Release Date: 2015-12-07
-  Changes:

   -  Updated documentation
   -  Made version 1.0.0, as this has been running successfully in
      several production environments.

Version 0.11.0
--------------

-  Release Date: 2015-12-06
-  Changes

   -  Initial port of
      `sentry-jira <https://github.com/getsentry/sentry-jira>`__ to
      `sentry-unfuddle <https://github.com/rkeilty/sentry-unfuddle>`__
