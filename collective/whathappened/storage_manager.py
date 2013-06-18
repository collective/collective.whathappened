from zope import interface
from zope import schema
from zope import component

from plone.registry.interfaces import IRegistry

from collective.whathappened import storage_backend

class IStorageManager(storage_backend.IStorageBackend):
    """The storage manager provide a complete API to manage notifications.
    It's a wrapper around the storage backend responsible to choose the
    backend to use.

    This design make it simple to code another backend without changing
    anything more than just a record in portal_registry.
    """

    backend = schema.TextLine(title=u"Backend name")

class StorageManager(object):
    interface.implements(IStorageManager)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.backend = None
        self.registry = None

    def update(self):
        if self.backend is None:
            self.registry = component.queryUtility(IRegistry)
            if self.registry is None:
                return
            backend = self.registry.get(
                'collective.whathappened.backend',
                'collective.whathappened.backend.sqlite',
            )
            self.backend = self.context.restrictedTraverse(backend)

    def initialize(self):
        self.update()
        if self.backend is None:
            return
        return self.backend.initialize()

    def terminate(self):
        self.update()
        if self.backend is None:
            return
        return self.backend.terminate()

    def store(self, notification):
        self.update()
        if self.backend is None:
            return
        return self.backend.store(notification)

    def getHot(self):
        self.update()
        if self.backend is None:
            return
        return self.backend.getHot()

    def getAll(self):
        self.update()
        if self.backend is None:
            return
        return self.backend.getAll()

    def setSeen(self, notification):
        self.update()
        if self.backend is None:
            return
        return self.backend.setSeen(notification)

    def clean(self):
        self.update()
        if self.backend is None:
            return
        return self.backend.clean()

    def getUnseenCount(self):
        self.update()
        if self.backend is None:
            return
        return self.backend.getUnseenCount()

    def getLastNotificationTime(self):
        self.update()
        if self.backend is None:
            return
        return self.backend.getLastNotificationTime()
