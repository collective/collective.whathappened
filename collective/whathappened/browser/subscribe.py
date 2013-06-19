from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.layout.viewlets import common

from collective.whathappened.subscription import Subscription
from collective.whathappened.storage_manager import StorageManager

class SubscribeViewlet(common.ViewletBase):
    def update(self):
        super(SubscribeViewlet, self).update()
        path = '/'.join(self.context.getPhysicalPath())
        storage = StorageManager(self.context, self.request)
        storage.initialize()
        subscription = storage.getSubscription(path)
        storage.terminate()
        if subscription is None:
            self.subscribed = False
        else:
            self.subscribed = subscription.wants


class Subscribe(BrowserView):
    def __call__(self):
        status = IStatusMessage(self.request)
        path = '/'.join(self.context.getPhysicalPath())
        storage = StorageManager(self.context, self.request)
        storage.initialize()
        try:
            storage.saveSubscription(Subscription(path, True))
            status.add(u"You have suscribed to %s" % path)
        except:
            status.add(u"Error while subscribing to %s" % path)
        storage.terminate()
        self.request.response.redirect(self.context.absolute_url())


class Unsubscribe(BrowserView):
    def __call__(self):
        status = IStatusMessage(self.request)
        path = '/'.join(self.context.getPhysicalPath())
        storage = StorageManager(self.context, self.request)
        storage.initialize()
        try:
            storage.saveSubscription(Subscription(path, False))
            status.add(u"You have unsuscribed from %s" % path)
        except:
            status.add(u"Error while unsubscribing from %s" % path)
        storage.terminate()
        self.request.response.redirect(self.context.absolute_url())
