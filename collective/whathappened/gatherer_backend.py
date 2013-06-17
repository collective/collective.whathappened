from zope import interface
from zope import schema
from zope import component

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

class IGathererBackend(interface.Interface):
    """A gatherer backend is a named utility able to get important information
    for a specific user and to transform it into notifications"""

    id = schema.ASCIILine(title=u"id")

    def getNewNotifications(lastCheck):
        """Get a list of new notifications since lastCheck.
        lastCheck is a datetime object."""

    def getId():
        """Get the unique id of the gatherer"""


class UserActionGathererBackend(BrowserView):
    """Create notifications from useraction (from collective.history)"""
    interface.implements(IGathererBackend)

    id = "useraction"

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.mtool = getToolByName(self.context, 'portal_membership')
        self.user = self.mtool.getAuthenticatedMember().getId()

    def getNewNotifications(self, lastCheck):
        return []

    def getId(self):
        return self.id
