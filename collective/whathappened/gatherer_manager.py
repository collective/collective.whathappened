from zope import interface
from zope import schema
from zope import component

from plone.registry.interfaces import IRegistry

from collective.whathappened.gatherer_backend import IGathererBackend

class IGathererManager(interface.Interface):
    """The gatherer manager provide a complete API to manage the creation of
    notifications. It's a wrapper around backend gatherers responsible to
    choose the backends to use.

    This design make it simple to code another backend without changing
    anything more than just a record in portal_registry.
    """


class GathererManager(object):
    interface.implements(IGathererManager)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.backends = []
        utilities = component.getUtilitiesFor(IGathererBackend)
        for utility in utilities:
            name, backend = utility
            self.backends.append(backend)

    def getNewNotifications(self, lastCheck):
        notifications = []
        for backend in self.backends:
            notifications.append(backend.getNewNotifications(lastCheck))
        return notifications
