class NoBackendException(Exception):
    def __init__(self, manager):
        self.manager = manager

    def __str__(self):
        return '%s: no backend could be found.' % self.manager

class NoStorageException(Exception):
    def __str__(self):
        return 'Could not get Storage Manager.'
