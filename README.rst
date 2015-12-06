sentry-unfuddle
===========

A flexible extension for Sentry which allows you to create issues in Unfuddle based on sentry events.
It is based off the implementation for sentry-jira (https://github.com/getsentry/sentry-jira).

Attention
---------

Plugin is currently under active development and not considered stable for production use yet.

Installation
------------

pip install sentry-unfuddle

Configuration
-------------

Go to your project's configuration page (Projects -> [Project]) and select the
Unfuddle tab. Enter the Unfuddle credentials and Project configuration and save changes.
Filling out the form is a two step process (one to fill in data, one to select
project).


License
-------

sentry-unfuddle is licensed under the terms of the 3-clause BSD license.


Contributing
------------

All contributions are welcome, including but not limited to:

 - Documentation fixes / updates
 - New features (requests as well as implementations)
 - Bug fixes (see issues list)
