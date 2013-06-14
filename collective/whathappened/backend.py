from zope import interface

class IBackendStorage(interface.Interface):
    """ A backend storage is a named utility able to store and retrieve
    notification created from useraction for a specific user """

    def create(useraction, user):
        """create a new notification from useraction for user. The notification
        is not seen by default"""

    def getHot(user):
        """get all "hot" notifications. Hot notifications are notifications the
        user may be the more interested in"""

    def getAll(user):
        """get all notifications for the given user"""

    def setSeen(notification, user):
        """set seen to true for the given notification for the given user"""

    def clean(user):
        """remove old notifications. It is up to the implementation to decide
        what "old notification" are (e.g.: notifications older than 7 days)"""

    def getUnseenCount(user):
        """get number of unseen notification for the given user"""


class SqliteBackend(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def create(useraction, user):
        pass

    def getHot(user):
        pass

    def getAll(user):
        pass

    def setSeen(notification, user):
        pass

    def clean(user):
        pass

    def getUnseenCount(user):
        pass
