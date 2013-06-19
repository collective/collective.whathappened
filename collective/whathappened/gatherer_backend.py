import datetime

from zope import interface
from zope import schema
from zope import component
from DateTime import DateTime

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from collective.history.manager import UserActionManager
from collective.history.useraction import IUserAction

from .notification import Notification

class IGathererBackend(interface.Interface):
    """A gatherer backend is a named utility able to get important information
    for a specific user and to transform it into notifications"""

    id = schema.ASCIILine(title=u"id")

    def getNewNotifications(lastCheck):
        """Get a list of new notifications since lastCheck.
        lastCheck is a datetime object."""

    def getId():
        """Get the unique id of the gatherer"""

    def setUser(user):
        """Set the user the gatherer is working for (default is the authenticated one)"""


class UserActionGathererBackend(BrowserView):
    """Create notifications from useraction (from collective.history)"""
    interface.implements(IGathererBackend)

    id = "useraction"

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.mtool = getToolByName(self.context, 'portal_membership')
        self.user = self.mtool.getAuthenticatedMember().getId()
        self.manager = UserActionManager(self.context, self.request)
        self.manager.update()

    def _createNotificationFromUserAction(self, useraction):
        if not IUserAction.providedBy(useraction):
            return
        notification = Notification(
            useraction.what,
            useraction.where_path,
            useraction.when,
            useraction.who,
            str(self.user),
            str(self.getId())
        )
        return notification

    def getNewNotifications(self, lastCheck):
        brains = self.manager.search({
            'created': DateTime(lastCheck),
            'created_usage': 'range:min',
        })
        notifications = []
        for brain in brains:
            notification = self._createNotificationFromUserAction(brain.getObject())
            #@TODO: CHECK USER HAS SUBSCRIBED TO NOTIFICATION
            notifications.append(notification)
        return notifications

    def getId(self):
        return self.id

    def setUser(self, user):
        self.user = user
