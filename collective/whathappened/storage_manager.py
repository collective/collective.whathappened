import logging

from zope import interface
from zope import schema
from zope import component

from plone.registry.interfaces import IRegistry

from collective.whathappened import storage_backend
from collective.whathappened.exceptions import NoBackendException

logger = logging.getLogger('collective.whathappened')


class IStorageManager(storage_backend.IStorageBackend):
    """The storage manager provide a complete API to manage notifications
    and subscriptions. It's a wrapper around the storage backend responsible
    to choose the backend to use.

    This design make it simple to code another backend without changing
    anything more than just a record in portal_registry.
    """

    backend = schema.TextLine(title=u"Backend name")


class StorageManager(object):
    interface.implements(IStorageManager)

    def __init__(self, context, request = None):
        self.context = context
        self.request = request
        self.backend = None
        self.registry = None

    def update(self):
        """update is called automatically on every methods called.
        See __getattribute__"""
        if self.backend is None:
            self.registry = component.queryUtility(IRegistry)
            if self.registry is None:
                return
            backend = self.registry.get(
                'collective.whathappened.backend',
                'collective.whathappened.backend.sqlite',
            )
            self.backend = self.context.restrictedTraverse(backend)
            if self.backend is None:
                raise NoBackendException('Storage')
            if not self.backend.validateBackend():
                logger.warning('Storage backend is not valid,'
                               ' using NullBackend instead.')
                self.backend = storage_backend.NullBackend()

    def __getattribute__(self, name):
        """Automatically call self.update() when other methods are called"""
        if name not in ['update', 'backend', 'registry', 'context']:
            self.update()
        return object.__getattribute__(self, name)

    def initialize(self):
        return self.backend.initialize()

    def terminate(self):
        return self.backend.terminate()

    def storeNotification(self, notification):
        return self.backend.storeNotification(notification)

    def removeNotification(self, notification):
        return self.backend.removeNotification(notification)

    def getHotNotifications(self):
        return self.backend.getHotNotifications()

    def getAllNotifications(self):
        return self.backend.getAllNotifications()

    def setSeen(self, path):
        return self.backend.setSeen(path)

    def clean(self):
        return self.backend.clean()

    def getUnseenCount(self):
        return self.backend.getUnseenCount()

    def getLastNotificationTime(self):
        return self.backend.getLastNotificationTime()

    def setUser(self, user):
        return self.backend.setUser(user)

    def getUser(self):
        return self.backend.getUser()

    def saveSubscription(self, subscription):
        return self.backend.saveSubscription(subscription)

    def getSubscription(self, where):
        return self.backend.getSubscription(where)

    def getSubscriptions(self):
        return self.backend.getSubscriptions()
