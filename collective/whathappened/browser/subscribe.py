import sqlite3

from zope import component
from zope import interface

from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

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

    def can_blacklist():
        """doc"""

    def can_unblacklist():
        """doc"""

    def can_canonical_blacklist():
        """doc"""

    def can_canonical_unblacklist():
        """doc"""


class Subscribe(BrowserView):
    msgid_add = u"You have enabled notifications from ${path}."
    msgid_err = u"Error while enabling notifications from ${path}"
    action = True
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
        self.subscription_canonical = None
        self.plone_tools_loaded = False

    def __call__(self):
        self.update()
        self.storage.initialize()
        try:
            self.storage.saveSubscription(
                Subscription(self.context_path, self.action)
            )
            self.status.add(_(
                self.msgid_add,
                mapping={'path': self.context_path.decode('utf-8')}
            ))
        except sqlite3.IntegrityError:
            self.status.add(_(
                self.msgid_err,
                mapping={'path': self.context_path.decode('utf-8')}
            ))
        self.storage.terminate()
        self.request.response.redirect(self.nextURL())

    def nextURL(self):
        referer = self.request.get("HTTP_REFERER", None)
        if not referer:
            context_state = component.getMultiAdapter(
                (self.context, self.request),
                name=u'plone_context_state'
            )
            referer = context_state.view_url()
        return referer

    def update(self):
        self.initialize()
        if self.is_anon:
            return
        self.storage.initialize()
        self.checkSubscription()
        self.checkCanonicalSubscription()
        self.storage.terminate()

    def initialize(self):
        if not self.plone_tools_loaded:
            self.portal_state = component.getMultiAdapter(
                (self.context, self.request),
                name=u'plone_portal_state'
            )
            self.status = IStatusMessage(self.request)
            self.context_state = component.getMultiAdapter(
                (self.context, self.request),
                name="plone_context_state"
            )
        if self.storage is None:
            self.storage = StorageManager(self.context)
        if self.context_path is None:
            self.context_path = '/'.join(self.context.getPhysicalPath())
        if self.canonical is None:
            self.canonical = self.context_state.canonical_object()
        if self.is_default_page is None:
            self.is_default_page = self.context != self.canonical
        if self.is_anon is None:
            self.is_anon = self.portal_state.anonymous()

    def _getSubscribed(self, path):
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
        self.subscribed = self._getSubscribed(path)
        self.subscription = self.storage.getSubscription(path)
        if self._hasParentSubscription(path):
            self.subscribed_show = False
        else:
            self.subscribed_show = True

    def checkCanonicalSubscription(self):
        if self.is_default_page:
            path = '/'.join(self.canonical.getPhysicalPath())
            self.subscribed_canonical = self._getSubscribed(path)
            self.subscription_canonical = self.storage.getSubscription(path)
            if self._hasParentSubscription(path):
                self.subscribed_canonical_show = False
            else:
                self.subscribed_canonical_show = True

    def can_subscribe(self):
        self.update()
        if self.is_anon:
            return False
        cond2 = self.subscribed_show
        cond3 = not self.subscribed
        return cond2 and cond3

    def can_unsubscribe(self):
        self.update()
        if self.is_anon:
            return False
        cond2 = self.subscribed_show
        cond3 = self.subscribed
        return cond2 and cond3

    def can_canonical_subscribe(self):
        self.update()
        if self.is_anon:
            return False
        cond2 = self.subscribed_canonical_show
        cond3 = not self.subscribed_canonical
        cond4 = self.is_default_page
        return cond2 and cond3 and cond4

    def can_canonical_unsubscribe(self):
        self.update()
        if self.is_anon:
            return False
        cond2 = self.subscribed_canonical_show
        cond3 = self.subscribed_canonical
        cond4 = self.is_default_page
        return cond2 and cond3 and cond4

    def can_blacklist(self):
        self.update()
        if self.is_anon:
            return False
        cond1 = self.subscription is None
        cond2 = self.subscribed
        return cond1 or cond2

    def can_unblacklist(self):
        self.update()
        if self.is_anon:
            return False
        cond1 = self.subscription is not None
        cond2 = not self.subscribed
        return cond1 and cond2

    def can_canonical_blacklist(self):
        self.update()
        if self.is_anon:
            return False
        cond1 = self.subscription_canonical is None
        cond2 = self.subscribed_canonical
        cond3 = self.is_default_page
        return (cond1 or cond2) and cond3

    def can_canonical_unblacklist(self):
        self.update()
        if self.is_anon:
            return False
        cond1 = self.subscription_canonical is not None
        cond2 = not self.subscribed_canonical
        cond3 = self.is_default_page
        return cond1 and cond2 and cond3


class Unsubscribe(Subscribe):
    msgid_add = u"You have disabled notifications from ${path}"
    msgid_err = u"Error while disabling notifications from ${path}"
    action = None


class Blacklist(Subscribe):
    msgid_add = u"You have blocked notifications from ${path}"
    msgid_err = u"Error while blocking notifications from ${path}"
    action = False


class Unblacklist(Subscribe):
    msgid_add = u"You have stopped blocking notifications from ${path}"
    msgid_err = (u"Error while stopping the blockage of notifications "
                 u"from ${path}")
    action = None
