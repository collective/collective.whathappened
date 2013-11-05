from zope import interface
from zope import component

from plone.registry.interfaces import IRegistry

from collective.whathappened.exceptions import NoBackendException


class IGathererManager(interface.Interface):
    """The gatherer manager provide a complete API to manage the creation of
    notifications. It's a wrapper around backend gatherers responsible to
    choose the backends to use.

    This design make it simple to code another backend without changing
    anything more than just a record in portal_registry.
    """

    def update():
        """Get the gatherer backends."""

    def getNewNotifications(lastCheck):
        """Get all new notifications since lastCheck"""

    def setUser(user):
        """Change the user the gather works on"""


class GathererManager(object):
    interface.implements(IGathererManager)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.backends = []

    def update(self):
        if not self.backends:
            self.registry = component.queryUtility(IRegistry)
            if self.registry is None:
                return
            backend = self.registry.get(
                'collective.whathappened.gatherer',
                'collective.whathappened.gatherer.useraction'
            )
            self.backends = [self.context.restrictedTraverse(backend)]
            if backend is None:
                raise NoBackendException('Gatherer')

    def __getattribute__(self, name):
        """Automatically call self.update() when other methods are called"""
        if name not in ['update', 'registry', 'backends', 'context', 'request']:
            self.update()
        return object.__getattribute__(self, name)

    def getNewNotifications(self, lastCheck):
        notifications = []
        for backend in self.backends:
            notifications += backend.getNewNotifications(lastCheck)
        return notifications

    def setUser(self, user):
        for backend in self.backends:
            backend.setUser(user)
