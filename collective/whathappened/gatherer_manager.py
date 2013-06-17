from zope import interface
from zope import schema
from zope import component
from zope.publisher.interfaces.browser import IBrowserRequest

from plone.app.customerize import registration
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

    def update(self):
        if not self.backends:
            views = registration.getViews(IBrowserRequest)
            self.backends = [ view.factory(self.context, self.request) for view in views
                              if IGathererBackend.implementedBy(view.factory)]

    def getNewNotifications(self, lastCheck):
        self.update()
        notifications = []
        for backend in self.backends:
            notifications.append(backend.getNewNotifications(lastCheck))
        return notifications
