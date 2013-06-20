from zope.component import getMultiAdapter

from Products.Five.browser import BrowserView

from plone.app.layout.viewlets import common

from ..gatherer_manager import GathererManager
from ..storage_manager import StorageManager


class AllView(BrowserView):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.update()
        self.setPath()
        return self.index()

    def update(self):
        self.gatherer = GathererManager(self.context, self.request)
        self.storage = StorageManager(self.context, self.request)
        self.storage.initialize()
        self.updateNotifications()
        self.notifications = self.storage.getAllNotifications()
        self.storage.terminate()
        self.notificationsCount = len(self.notifications)

    def setPath(self):
        context = self.context.aq_inner
        portal_state = getMultiAdapter((context, self.request),
                                       name=u'plone_portal_state')
        path = portal_state.navigation_root().getPhysicalPath()
        self.navigation_root = '/'.join(path)

    def updateNotifications(self):
        #@TODO: GET LAST CHECK FROM SESSION OR STORAGE
        lastCheck = self.storage.getLastNotificationTime()
        newNotifications = self.gatherer.getNewNotifications(lastCheck)
        if newNotifications is not None:
            for notification in newNotifications:
                self.storage.storeNotification(notification)


class HotViewlet(common.ViewletBase):
    def update(self):
        self.setPath()
        self.gatherer = GathererManager(self.context, self.request)
        self.storage = StorageManager(self.context, self.request)
        self.storage.initialize()
        self.updateNotifications()
        self.notifications = self.storage.getHotNotifications()
        self.unseenCount = self.storage.getUnseenCount()
        self.storage.terminate()

    def setPath(self):
        context = self.context.aq_inner
        portal_state = getMultiAdapter((context, self.request),
                                       name=u'plone_portal_state')
        path = portal_state.navigation_root().getPhysicalPath()
        self.navigation_root = '/'.join(path)

    def updateNotifications(self):
        #@TODO: GET LAST CHECK FROM SESSION OR STORAGE
        lastCheck = self.storage.getLastNotificationTime()
        newNotifications = self.gatherer.getNewNotifications(lastCheck)
        if newNotifications is not None:
            for notification in newNotifications:
                self.storage.storeNotification(notification)
