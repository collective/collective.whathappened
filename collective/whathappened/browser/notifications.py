import datetime
from collections import OrderedDict

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from plone.app.layout.viewlets import common
from zope.component import getMultiAdapter
from zope.i18n import translate

from collective.whathappened.gatherer_manager import GathererManager
from collective.whathappened.storage_manager import StorageManager
from collective.whathappened.i18n import _
from collective.history.i18n import _ as _h

SESSION_LAST_CHECK = 'collective.whathappened.lastcheck'

_day = (_(u'Monday'),
        _(u'Tuesday'),
        _(u'Wednesday'),
        _(u'Thursday'),
        _(u'Friday'),
        _(u'Saturday'),
        _(u'Sunday'))

_month = (_(u'January'),
          _(u'February'),
          _(u'March'),
          _(u'April'),
          _(u'May'),
          _(u'June'),
          _(u'July'),
          _(u'August'),
          _(u'September'),
          _(u'October'),
          _(u'November'),
          _(u'December'))


class AllView(BrowserView):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.update()
        self.setPath()
        self.sortNotifications()
        return self.index()

    def update(self):
        self.gatherer = GathererManager(self.context, self.request)
        self.storage = StorageManager(self.context, self.request)
        self.storage.initialize()
        self.updateNotifications()
        self.notifications = self.storage.getAllNotifications()
        self.storage.terminate()
        self.notificationsCount = len(self.notifications)

    def show(self, notification):
        what = translate(_h(notification.what.decode("utf-8")),
                         domain="collective.history", context=self.request)
        where = notification.where.encode('utf-8')
        try:
            where = self.context.restrictedTraverse(where).Title()
        except KeyError:
            where = where.split('/')[-1]
        return _(u"${who} has ${what} ${where}",
                 mapping={
                     'who': ', '.join(notification.who),
                     'what': what,
                     'where': where,
                 })

    def sortNotifications(self):
        notifications = OrderedDict()
        for n in self.notifications:
            date = n.when.strftime('%s %%d %s' %
                                   (_day[n.when.weekday()],
                                    _month[n.when.month - 1]))
            if not notifications.has_key(date):
                notifications[date] = []
            notifications[date].append(n)
        self.notifications = notifications

    def setPath(self):
        context = self.context.aq_inner
        portal_state = getMultiAdapter((context, self.request),
                                       name=u'plone_portal_state')
        path = portal_state.navigation_root().getPhysicalPath()
        self.navigation_root = '/'.join(path)

    def updateNotifications(self):
        lastCheck = _getLastCheck(self.context, self.storage)
        newNotifications = self.gatherer.getNewNotifications(lastCheck)
        if newNotifications is not None:
            for notification in newNotifications:
                self.storage.storeNotification(notification)


class HotViewlet(common.PersonalBarViewlet):
    def update(self):
        super(HotViewlet, self).update()
        if self.anonymous:
            return
        self.setPath()
        self.gatherer = GathererManager(self.context, self.request)
        self.storage = StorageManager(self.context, self.request)
        self.storage.initialize()
        self.setSeen()
        self.updateNotifications()
        self.hotNotifications = self.storage.getHotNotifications()
        self.unseenCount = self.storage.getUnseenCount()
        self.storage.terminate()
        self.updateUserActions()

    def show(self, notification):
        what = translate(_h(notification.what.decode("utf-8")),
                         domain="collective.history", context=self.request)
        where = notification.where.encode('utf-8')
        try:
            where = self.context.restrictedTraverse(where).Title()
        except KeyError:
            where = where.split('/')[-1]
        return _(u"${who} has ${what} ${where}",
                 mapping={
                     'who': ', '.join(notification.who),
                     'what': what,
                     'where': where
                 })

    def setSeen(self):
        path = '/'.join(self.context.getPhysicalPath())
        self.storage.setSeen(path)

    def updateUserActions(self):
        if self.user_name is not None:
            self.user_name += " (%d)" % self.unseenCount
        portal = self.portal_state.portal()
        portal_path = '/'.join(portal.getPhysicalPath())
        self.notifications = []
        for notification in self.hotNotifications:
            path = notification.where[len(portal_path):]
            url = self.site_url + path
            title = self.show(notification)
            self.notifications.append({
                'title': title,
                'url': url,
                'seen': notification.seen
            })

    def updateNotifications(self):
        lastCheck = _getLastCheck(self.context, self.storage)
        newNotifications = self.gatherer.getNewNotifications(lastCheck)
        if newNotifications is not None:
            for notification in newNotifications:
                self.storage.storeNotification(notification)

    def setPath(self):
        context = self.context.aq_inner
        portal_state = getMultiAdapter((context, self.request),
                                       name=u'plone_portal_state')
        path = portal_state.navigation_root().getPhysicalPath()
        self.navigation_root = '/'.join(path)


def _getLastCheck(context, storage):
    sdm = getToolByName(context, 'session_data_manager')
    session = sdm.getSessionData()
    if session is None or not session.has_key(SESSION_LAST_CHECK):
        lastCheck = storage.getLastNotificationTime()
    else:
        lastCheck = session[SESSION_LAST_CHECK]
    session[SESSION_LAST_CHECK] = datetime.datetime.now()
    return lastCheck
