Introduction
============

Collective.whathappened allows you to creates notifications from various events. Notifications are only created when the user check them. User can subscribe to paths to choose their notifications. There are two main interfaces which can be changed to modify the behaviour of this module.

The Gatherer backend gathers the information you want. It also create the Notifications and send them to the storage manager (c.f. next paragraph). The default gatherer works with User Action from collective.history. There can be more than one gatherer working at a time.

The Storage backend is responsible for storing notifications and subscribe information per user. The default storage creates a Sqlite databases for each user. The "collective_whathappened_sqlite_directory" variable must be set in the buildout configuration. Please see configuration chapter for more information.

Configuration
=============

Defaut storage backend use "collective_whathappened_sqlite_directory" variable to know where to store the Sqlite databases. It should be added in the buildout configuration file. For example:

  [instance]
  environment-vars +=
      collective_whathappened_sqlite_directory ${buildout:directory}/var/sqlite

How to install
==============

This addon can be installed has any other addons. please follow official
documentation_

Credits
=======

Companies
---------

* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact Makina Corpus <mailto:python@makina-corpus.org>`_

People
------

- JeanMichel FRANCOIS aka toutpt <toutpt@gmail.com>
- Gagaro <gagaro42@gmail.com>

.. _documentation: http://plone.org/documentation/kb/installing-add-ons-quick-how-to
