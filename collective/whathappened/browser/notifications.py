import datetime
from collections import OrderedDict

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from plone.app.layout.viewlets import common
from zope.component import getMultiAdapter
from zope import component
from zope.i18nmessageid import MessageFactory
from zope.i18n import translate

from collective.whathappened.gatherer_manager import GathererManager
from collective.whathappened.storage_manager import StorageManager
from collective.whathappened.i18n import _
from collective.whathappened.utility import IDisplay
from collective.history.i18n import _ as _h

PLMF = MessageFactory('plonelocales')
SESSION_LAST_CHECK = 'collective.whathappened.lastcheck'


def show(context, request, notification):
    utility = component.queryUtility(IDisplay,
				     name=notification.what)
    if utility is None:
        utility = component.getUtility(IDisplay,
				       name='default_display')
    return utility.display(context, request, notification)


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
        return show(self.context, self.request, notification)

    def sortNotifications(self):
        notifications = OrderedDict()
        ts = getToolByName(self.context, 'translation_service')
        for n in self.notifications:
            weekday = (n.when.weekday() + 1) % 7
            day = translate(PLMF(ts.day_msgid(weekday),
                                 default=ts.weekday_english(weekday)))
            month = translate(PLMF(ts.month_msgid(n.when.month),
                                   default=ts.month_english(n.when.month)))
            date = n.when.strftime('%s %%d %s' %
                                   (day, month))
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
        return show(self.context, self.request, notification)

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
