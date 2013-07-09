import sqlite3

from zope import component
from zope import interface

from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.layout.viewlets import common

from collective.whathappened.subscription import Subscription
from collective.whathappened.storage_manager import StorageManager
from collective.whathappened.i18n import _


class ISubscribe(interface.Interface):

    def can_subscribe():
        """doc"""

    def can_unsubscribe():
        """doc"""

    def can_canonical_subscribe():
        """doc"""

    def can_canonical_unsubscribe():
        """doc"""


class Subscribe(BrowserView):
    msgid_add = u"You have subscribed to ${path}."
    msgid_err = u"Error while subscribing to ${path}"
    subscription = True
    interface.implements(ISubscribe)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.storage = None
        self.status = None
        self.portal_state = None
        self.context_path = None
        self.context_state = None
        self.is_anon = None
        self.is_default_page = None
        self.subscribed_show = False
        self.canonical = None
        self.subscribed_canonical = None
        self.subscribed_canonical_show = False

    def __call__(self):
        self.update()
        self.storage.initialize()
        try:
            self.storage.saveSubscription(
                Subscription(self.context_path, self.subscription)
            )
            self.status.add(
                _(self.msgid_add,
                mapping={'path': self.context_path.decode('utf-8')})
            )
        except sqlite3.IntegrityError:
            self.status.add(_(self.msgid_err,
                         mapping={'path': self.context_path.decode('utf-8')}))
        self.storage.terminate()
        self.request.response.redirect(self.context.absolute_url())

    def update(self):
        self.initialize()
        self.storage.initialize()
        self.checkSubscription()
        self.checkCanonicalSubscription()
        self.storage.terminate()

    def initialize(self):
        if self.portal_state is None:
            self.portal_state = component.getMultiAdapter(
                (self.context, self.request),
                name=u'plone_portal_state'
            )
        if self.storage is None:
            self.storage = StorageManager(self.context, self.request)
        if self.status is None:
            self.status = IStatusMessage(self.request)
        if self.context_path is None:
            self.context_path = '/'.join(self.context.getPhysicalPath())
        if self.context_state is None:
            self.context_state = component.getMultiAdapter(
                (self.context, self.request),
                name="plone_context_state"
            )
        if self.canonical is None:
            self.canonical = self.context_state.canonical_object()
        if self.is_default_page is None:
            self.is_default_page = self.context != self.canonical
        if self.is_anon is None:
            self.is_anon = self.portal_state.anonymous()

    def _getSubscription(self, path):
        subscription = self.storage.getSubscription(path)

        if subscription is None:
            return False

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

    def can_subscribe(self):
        self.update()
        cond1 = not self.is_anon
        cond2 = self.subscribed_show
        cond3 = not self.subscribed
        return cond1 and cond2 and cond3

    def can_unsubscribe(self):
        self.update()
        cond1 = not self.is_anon
        cond2 = self.subscribed_show
        cond3 = self.subscribed
        return cond1 and cond2 and cond3

    def can_canonical_subscribe(self):
        self.update()
        cond1 = not self.is_anon
        cond2 = self.subscribed_canonical_show
        cond3 = not self.subscribed_canonical
        cond4 = self.is_default_page
        return cond1 and cond2 and cond3 and cond4

    def can_canonical_unsubscribe(self):
        self.update()
        cond1 = not self.is_anon
        cond2 = self.subscribed_canonical_show
        cond3 = self.subscribed_canonical
        cond4 = self.is_default_page
        return cond1 and cond2 and cond3 and cond4


class Unsubscribe(Subscribe):
    msgid_add = u"You have unsubscribed from ${path}"
    msgid_err = u"Error while unsubscribing from ${path}"
    subscription = False
