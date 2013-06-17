from zope import interface
from zope import schema
from Products.CMFCore.utils import getToolByName

class IGathererBackend(interface.Interface):
    """A gatherer backend is a named utility able to get important information
    for a specific user and to transform it into notifications"""

    id = schema.ASCIILine(title=u"id")

    def getNewNotifications():
        """Get a list of new notifications since lastCheck.
        lastCheck is a datetime object."""

    def getId():
        """Get the unique id of the gatherer"""


class UserActionGathererBackend(object):
    """Create notifications from useraction (from collective.history)"""

    id = "useraction"

    def __init__(self):
        pass
#        self.mtool = getToolByName(self, 'portal_membership')
#        self.user = getAuthenticatedMember().getId()

    def getNewNotifications(self, lastCheck):
        return []

    def getId(self):
        return self.id
