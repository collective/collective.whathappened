import json

from AccessControl.unauthorized import Unauthorized

from zope import interface
from zope import schema
from DateTime import DateTime

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from collective.history.manager import UserActionManager
from collective.history.useraction import IUserAction

from collective.whathappened.notification import Notification
from collective.whathappened.storage_manager import StorageManager


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
        """Set the user the gatherer is working for
        (default is the authenticated one)"""


class UserActionGathererBackend(BrowserView):
    """Create notifications from useraction (from collective.history)"""
    interface.implements(IGathererBackend)

    id = "useraction"

    def __init__(self, context, request):
        self.context = context
        self.request = request
        settings_url = '@@get-whathappened-settings'
        self.settings = self.context.restrictedTraverse(settings_url)()
        self.mtool = getToolByName(self.context, 'portal_membership')
        self.user = self.mtool.getAuthenticatedMember().getId()
        self.manager = UserActionManager(self.context, self.request)
        self.manager.update()
        self.storage = StorageManager(self.context, self.request)

    def _createNotificationFromUserAction(self, useraction):
        if not IUserAction.providedBy(useraction):
            return
        try:
            info = json.loads(useraction.what_info)
        except:
            info = None
        notification = Notification(
            useraction.what,
            useraction.where_path,
            useraction.when,
            [useraction.who],
            str(self.user),
            str(self.getId()),
            info=info
        )
        return notification

    def _getSubscriptionInTree(self, path):
        while '/' in path and path != '/':
            subscription = self.storage.getSubscription(path)
            if subscription is not None:
                break
            path = path.rpartition('/')[0]
        return subscription

    def getNewNotifications(self, lastCheck):
        brains = self.manager.search(when={
            'query': DateTime(lastCheck),
            'range': 'min'
        })
        notifications = []
        self.storage.initialize()
        for brain in brains:
            subscription = self._getSubscriptionInTree(brain.where_path)
            if not self._useractionIsCorrect(subscription, brain, lastCheck):
                continue
            useraction = self.manager.get(brain.id)
            if useraction.who == self.user:
                continue
            notification = self._createNotificationFromUserAction(useraction)
            notifications.append(notification)
        self.storage.terminate()
        return notifications

    def _useractionIsCorrect(self, subscription, brain, lastCheck):
        what_whitelist = self.settings.useraction_gatherer_whitelist
        if subscription is None or not subscription.wants:
            return False
        if brain.when < lastCheck:
            return False
        if brain.what not in what_whitelist:
            return False
        try:
            self.context.restrictedTraverse(brain.where_path)
        except Unauthorized:
            return False
        except KeyError:
            return False
        except AttributeError:
            return False
        return True

    def getId(self):
        return self.id

    def setUser(self, user):
        self.user = user
        self.storage.setUser(user)
