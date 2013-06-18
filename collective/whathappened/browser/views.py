from Products.Five.browser import BrowserView

from ..gatherer_manager import GathererManager
from ..storage_manager import StorageManager


class All(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        self.gatherer = GathererManager(self.context, self.request)
        self.storage = StorageManager(self.context, self.request)

        self.storage.initialize()
        self.updateNotifications()
        self.notifications = self.storage.getAll()
        self.storage.terminate()
        self.notificationsCount = len(self.notifications)

    def updateNotifications(self):
        #GET LAST CHECK FROM SESSION OR STORAGE
        lastCheck = self.storage.getLastNotificationTime()
        newNotifications = self.gatherer.getNewNotifications(lastCheck)
        if newNotifications is not None:
            for notification in newNotifications:
                self.storage.store(notification)
