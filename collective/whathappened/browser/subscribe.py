from zope import component

from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.layout.viewlets import common

from collective.whathappened.subscription import Subscription
from collective.whathappened.storage_manager import StorageManager
from collective.whathappened.i18n import _

class SubscribeViewlet(common.ViewletBase):
    def update(self):
        super(SubscribeViewlet, self).update()
        self.initialize()
        self.storage.initialize()
        self.checkSubscription()
        self.checkCanonicalSubscription()
        self.storage.terminate()

    def initialize(self):
        self.storage = StorageManager(self.context, self.request)
        context_state = component.getMultiAdapter((self.context, self.request),
                                                  name="plone_context_state")
        self.canonical = context_state.canonical_object()
        self.is_default_page = self.context != self.canonical

    def _getSubscription(self, path):
        subscription = self.storage.getSubscription(path)
        if subscription is None:
            return False
        else:
            return subscription.wants

    def _hasParentSubscription(self, path):
        path = path.rpartition('/')[0]
        while len(path) > 0 and path != '/':
            if '/' not in path:
                break
            subscription = self.storage.getSubscription(path)
            if subscription is not None and subscription.wants:
                return True
            path = path.rpartition('/')[0]
        return False

    def checkSubscription(self):
        path = '/'.join(self.context.getPhysicalPath())
        self.subscribed = self._getSubscription(path)
        if self._hasParentSubscription(path):
            self.subscribed_show = False
        else:
            self.subscribed_show = True

    def checkCanonicalSubscription(self):
        if self.is_default_page:
            path = '/'.join(self.canonical.getPhysicalPath())
            self.subscribed_canonical = self._getSubscription(path)
            if self._hasParentSubscription(path):
                self.subscribed_canonical_show = False
            else:
                self.subscribed_canonical_show = True


class Subscribe(BrowserView):
    def __call__(self):
        status = IStatusMessage(self.request)
        path = '/'.join(self.context.getPhysicalPath())
        storage = StorageManager(self.context, self.request)
        storage.initialize()
        try:
            storage.saveSubscription(Subscription(path, True))
            status.add(_(u"You have suscribed to ${path}.",
                         mapping={'path': path.decode('utf-8')}))
        except:
            status.add(_(u"Error while subscribing to ${path}",
                         mapping={'path': path.decode('utf-8')}))
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
            status.add(_(u"You have unsuscribed from ${path}",
                         mapping={'path': path.decode('utf-8')}))
        except:
            status.add(_(u"Error while unsubscribing from ${path}",
                         mapping={'path': path.decode('utf-8')}))
        storage.terminate()
        self.request.response.redirect(self.context.absolute_url())
