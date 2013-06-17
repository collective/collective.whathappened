import datetime
from zope import interface
from Products.CMFCore.utils import getToolByName

class IStorageBackend(interface.Interface):
    """A storage backend is a named utility able to store and retrieve
    notifications"""

    def store(notification):
        """store a notification"""

    def getHot():
        """get all "hot" notifications. Hot notifications are notifications the
        user may be the more interested in"""

    def getAll():
        """get all notifications"""

    def setSeen(notification):
        """set seen to true for the given notification and save it"""

    def clean():
        """remove old notifications. It is up to the implementation to decide
        what "old notification" are (e.g.: notifications older than 7 days)"""

    def getUnseenCount():
        """get number of unseen notification"""

    def getLastNotificationTime():
        """get the date and time of the last notification

        Return: a datetime object"""


class SqliteStorageBackend(object):
    interface.implements(IStorageBackend)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.mtool = getToolByName(self.context, 'portal_membership')
        self.user = self.mtool.getAuthenticatedMember().getId()

    def store(self, notification):
        pass

    def getHot(self):
        pass

    def getAll(self):
        return []

    def setSeen(self, notification):
        pass

    def clean(self):
        pass

    def getUnseenCount(self):
        pass

    def getLastNotificationTime(self):
        #TODO get real time from last notification
        lastTime = datetime.datetime.now() - datetime.timedelta(7)
        return lastTime
