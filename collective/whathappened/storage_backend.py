import datetime
import time
import os
import sqlite3

from zope import interface
from Products.CMFCore.utils import getToolByName

from .notification import Notification
from .subscription import Subscription

class IStorageBackend(interface.Interface):
    """A storage backend is a named utility able to store and retrieve
    notifications and subscriptions for a specific user
    (the authenticated one by default)."""

    def initiliaze():
        """Initialize the storage backend to start a storage session."""

    def terminate():
        """Finish a storage session."""

    def setUser(user):
        """change the user the storage is working on."""

    def getUser():
        """get the user the storage is working on."""

    def storeNotification(notification):
        """Store a notification."""

    def getHotNotifications():
        """Get all "hot" notifications. Hot notifications are notifications the
        user may be the more interested in."""

    def getAllNotifications():
        """Get all notifications."""

    def setSeen(notification):
        """Set seen to true for the given notification and save it."""

    def getUnseenCount():
        """Get number of unseen notification."""

    def getLastNotificationTime():
        """Get the date and time of the last notification.

        Return: a datetime object"""

    def clean():
        """Remove old notifications. It is up to the implementation to decide
        what "old notification" are (e.g.: notifications older than 7 days)."""

    def saveSubscription(subscription):
        """Store a subscription or update it."""

    def getSubscription(where):
        """Get the subscription corresponding to 'where'."""

    def getSubscriptions():
        """Get all subscriptions of the user."""


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
            '''
            CREATE TABLE IF NOT EXISTS notifications(
            `what`      TEXT,
            `when`      INTEGER,
            `where`     TEXT,
            `who`       TEXT,
            `seen`      INTEGER,
            `gatherer`  TEXT,
            PRIMARY KEY(`what`, `when`, `where`, `who`))
            '''
        )
        self.db.execute(
            '''
            CREATE TABLE IF NOT EXISTS subscriptions(
            `where`     TEXT PRIMARY KEY,
            `wants`     INTEGER)
            '''
        )

    def terminate(self):
        self.db.commit()
        self.db.close()
        self.db = None

    def storeNotification(self, notification):
        if self.db is None:
            return
        try:
            self.db.execute(
                "INSERT INTO notifications VALUES (?, ?, ?, ?, ?, ?)",
                [notification.what,
                 notification.getWhenTimestamp(),
                 notification.where,
                 notification.who,
                 notification.seen,
                 notification.gatherer]
            )
        except sqlite3.IntegrityError:
            pass

    def getHotNotifications(self):
        if self.db is None:
            return []
        results = self.db.execute(
            """
            SELECT * FROM notifications
            ORDER BY `seen` ASC, `when` DESC
            LIMIT 5
            """
        ).fetchall()
        notifications = []
        for result in results:
            notifications.append(self._createNotificationFromResult(result))
        return notifications

    def _createNotificationFromResult(self, result):
        notification = Notification(
            result[0],
            result[2],
            datetime.datetime.fromtimestamp(result[1]),
            result[3],
            self.user,
            result[4],
            result[5],
        )
        return notification

    def getAllNotifications(self):
        if self.db is None:
            return []
        results = self.db.execute(
            """
            SELECT * FROM notifications
            ORDER BY `when` DESC
            """
        ).fetchall()
        notifications = []
        for result in results:
            notifications.append(self._createNotificationFromResult(result))
        return notifications

    def setSeen(self, notification):
        try:
            self.db.execute(
                """
                UPDATE notifications
                SET seen = 1
                WHERE
                    `what` = ? AND
                    `where` = ? AND
                    `when` = ? AND
                    `who` = ?
                """,
                [notification.what,
                 notification.where,
                 notification.when,
                 notification.who]
            )
        except:
            pass

    def clean(self):
        lastWeek = datetime.datetime.now() - datetime.timedelta(7)
        timestamp = time.mktime(lastWeek.timetuple())
        self.db.execute("REMOVE FROM notifications WHERE `when` < ?", [timestamp])

    def getUnseenCount(self):
        if self.db is None:
            return 0
        query = self.db.execute("SELECT COUNT(*) FROM notifications WHERE `seen` = 0")
        unseen = query.fetchone()[0]
        return unseen

    def getLastNotificationTime(self):
        try:
            req = "SELECT `when` FROM notifications ORDER BY `when` DESC LIMIT 1"
            result = self.db.execute(req).fetchone()
            lastTime = datetime.datetime.fromtimestamp(result[0])
        except:
            lastTime = datetime.datetime.now() - datetime.timedelta(7)
        return lastTime

    def saveSubscription(self, subscription):
        try:
            self.db.execute("INSERT INTO subscriptions VALUES (?, ?)",
                            [subscription.where, subscription.wants])
        except sqlite3.IntegrityError:
            self.db.execute("UPDATE subscriptions SET `wants` = ? WHERE `where` = ?",
                            [subscription.wants, subscription.where])

    def _createSubscriptionFromResult(self, result):
        wants = result[1] == 1
        subscription = Subscription(result[0], wants)
        return subscription

    def getSubscription(self, where):
        results = self.db.execute("SELECT * FROM subscriptions WHERE `where` = ?",
                                  [where]).fetchall()
        if len(results) == 0:
            return None
        return self._createSubscriptionFromResult(results[0])

    def getSubscriptions(self):
        results = self.db.execute("SELECT * FROM subscriptions").fetchall()
        subscriptions = []
        for result in results:
            subscriptions.append(self._createSubscriptionFromResult(result))
        return subscriptions

    def setUser(self, user):
        if self.db is not None:
            return
        self.user = user

    def getUser(self):
        return self.user
