import datetime
import time
import os
import sqlite3

from zope import interface
from Products.CMFCore.utils import getToolByName

from .notification import Notification

class IStorageBackend(interface.Interface):
    """A storage backend is a named utility able to store and retrieve
    notifications"""

    def initiliaze():
        """Initialize the storage backend to start a storage session"""

    def terminate():
        """Finish a storage session"""

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
        directory = os.environ.get('collective_whathappened_sqlite_directory', None)
        self.db_path = os.path.join(directory,  '%s.sqlite' % self.user)
        self.db = None

    def initialize(self):
        self.db = sqlite3.connect(self.db_path)
        self.db.execute(
            '''CREATE TABLE IF NOT EXISTS notifications(
            `what`        TEXT,
            `when`        INTEGER,
            `where`       TEXT,
            `who`         TEXT,
            `gatherer`    TEXT)'''
        )

    def terminate(self):
        self.db.commit()
        self.db.close()
        self.db = None

    def store(self, notification):
        if self.db is None:
            return
        self.db.execute(
            "INSERT INTO notifications VALUES (?, ?, ?, ?, ?)",
            (notification.what,
            notification.getWhenTimestamp(),
            notification.where,
            notification.who,
            notification.gatherer)
        )

    def getHot(self):
        if self.db is None:
            return []
        return []

    def _createNotificationFromResult(self, result):
        notification = Notification(
            result[0],
            result[2],
            datetime.datetime.fromtimestamp(result[1]),
            result[3],
            self.user,
            result[4],
        )
        return notification

    def getAll(self):
        if self.db is None:
            return []
        results = self.db.execute("SELECT * FROM notifications").fetchall()
        notifications = []
        for result in results:
            notifications.append(self._createNotificationFromResult(result))
        return notifications

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
