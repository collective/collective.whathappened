from zope import interface
from zope import schema
from zope import component

from plone.registry.interfaces import IRegistry

from collective.whathappened import backend

class INotificationManager(backend.IBackendStorage):
    """The notification manager provide a complete API to manage notifications.
    It's a wrapper around the backend storage responsible to choose the
    backend to use.

    This design make it simple to code an other backend without changing
    anything more than just a record in portal_registry.
    """

    backend = schema.TextLine(title=u"Backend name")

class NotificationManager(object):
    interface.implements(INotificationManager)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.registry = component.queryUtility(IRegistry)
        if self.registry is None:
            return
        backend = self.registry.get(
            'collective.whathappened.backend',
            'collective.whathappened.backend.sqlite',
        )
        self.backend = self.context.restrictedTraverse(backend)

    def create(self, useraction, user):
        if self.backend is None:
            return
        return self.backend.create(useraction, user)

    def getHot(self, user):
        if self.backend is None:
            return
        return self.backend.getHot(user)

    def getAll(self, user):
        if self.backend is None:
            return
        return self.backend.getAll(user)

    def setSeen(self, notification, user):
        if self.backend is None:
            return
        return self.backend.setSeen(notification, user)

    def clean(self, user):
        if self.backend is None:
            return
        return self.backend.clean(user)

    def getUnseenCount(self, user):
        if self.backend is None:
            return
        return self.backend.getUnseenCount(user)
