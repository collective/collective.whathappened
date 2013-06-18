import os
from zope.configuration.exceptions import ConfigurationError

sqlite_directory = os.environ.get('collective_whathappened_sqlite_directory', None)

if sqlite_directory is None:
    raise ConfigurationError("collective_whathappened_sqlite_directory is not set.")

if not os.path.exists(sqlite_directory):
    os.makedirs(sqlite_directory, 0775)

if os.path.exists(sqlite_directory) and not os.path.isdir(sqlite_directory):
    raise ConfigurationError("%s exists but is not a directory." % sqlite_directory)
