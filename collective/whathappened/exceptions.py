

class NoBackendException(Exception):
    def __init__(self, manager):
        self.manager = manager

    def __str__(self):
        return '%s: no backend could be found.' % self.manager


class NoStorageException(Exception):
    def __str__(self):
        return 'Could not get Storage Manager.'


class NotificationValueError(ValueError):
    def __init__(self, notification):
        ValueError.__init__(self)
        self.notification = notification

    def __str__(self):
        return "the notification value is not good enough to be displayed"
