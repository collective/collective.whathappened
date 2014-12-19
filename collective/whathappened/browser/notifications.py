import datetime
import logging
import urllib

from collections import OrderedDict

from AccessControl.unauthorized import Unauthorized

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from plone.app.layout.viewlets import common
from plone.app.redirector.interfaces import IRedirectionStorage
from zope.component import getMultiAdapter, queryUtility
from zope.browser.interfaces import IBrowserView
from zope import component
from zope.i18nmessageid import MessageFactory
from zope.i18n import translate

from collective.whathappened.gatherer_manager import GathererManager
from collective.whathappened.storage_manager import StorageManager
from collective.whathappened.utility import IDisplay
from collective.whathappened.exceptions import NotificationValueError

PLMF = MessageFactory('plonelocales')
SESSION_LAST_CHECK = 'collective.whathappened.lastcheck'


def show(context, request, notification):
    utility = component.queryUtility(IDisplay, name=notification.what)
    if utility is None:
        utility = component.getUtility(IDisplay, name='default_display')
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
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.getAuthenticatedMember().getId() is None:
            raise Unauthorized
        self.gatherer = GathererManager(self.context, self.request)
        self.storage = StorageManager(self.context, self.request)
        self.storage.initialize()
        self.updateNotifications()
        self.notifications = self.storage.getAllNotifications()
        self._validate_notifications()
        self.storage.terminate()
        self.notificationsCount = len(self.notifications)

    def _validate_notifications(self):
        for notification in self.notifications:
            try:
                validateNotification(self.context, notification)
            except NotificationValueError:
                self.storage.removeNotification(notification)
                self.notifications.remove(notification)

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
            if not date in notifications:
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


class SetAllSeen(BrowserView):
    def __call__(self):
        storage = StorageManager(self.context, self.request)
        storage.initialize()
        storage.setSeen()
        storage.terminate()
        url = '@@collective_whathappened_notifications_all'
        self.request.response.redirect(url)


class HotViewlet(common.PersonalBarViewlet):
    def update(self):
        super(HotViewlet, self).update()
        if self.anonymous:
            return
        self.storage = StorageManager(self.context, self.request)
        self.storage.initialize()
        #self.setSeen()
        self.storage.terminate()
        self.notifications = getHotNotifications(self.context, self.request)
        self.unseenCount = getUnseenCount(self.context, self.request)
        self.storage.initialize()
        self.updateUserActions()
        self.storage.terminate()

    def setSeen(self):
        #path = '/'.join(self.context.getPhysicalPath())
        portal_path = '/'.join(self.portal_state.portal().getPhysicalPath())
        portal_url = self.portal_state.portal_url()
        path = self.request['ACTUAL_URL'][len(portal_url):]
        if not path.startswith(portal_path):
            path = portal_path + path
        self.storage.setSeen(path)

    def updateUserActions(self):
        if self.user_name is not None:
            self.user_name += " (%d)" % self.unseenCount


def getUnseenCount(context, request):
    storage = StorageManager(context, request)
    storage.initialize()
    unseenCount = storage.getUnseenCount()
    storage.terminate()
    return unseenCount


def validateNotification(context, notification):
    path = notification.where
    content = None
#        if path.startswith(portal_path):
#            path = path[len(portal_path)+1:]
    try:
        content = context.restrictedTraverse(str(path))
    except Unauthorized:
        # Can't view the content anymore. Delete the notification.
        raise NotificationValueError(notification)
    except KeyError:
        # The content have been moved or removed try to find it
        redirection_storage = queryUtility(IRedirectionStorage)
        if redirection_storage is None:
            raise NotificationValueError(notification)
        old_path = str(path)  # Whole path needed (with portal_path)
        new_path = redirection_storage.get(old_path)
        if new_path:
            try:
                content = context.restrictedTraverse(new_path)
            except KeyError:
                raise NotificationValueError(notification)
        else:
            raise NotificationValueError(notification)
    except Exception, e:
        logging.getLogger(__name__).error(e)
        raise NotificationValueError(notification)

    return content


def getHotNotifications(context, request):
    gatherer = GathererManager(context, request)
    storage = StorageManager(context, request)
    storage.initialize()
    _updateNotifications(context, storage, gatherer)
    hotNotifications = storage.getHotNotifications()
    #portal_path = _getPortalPath(context, request)
    notifications = []

    for notification in hotNotifications:
        try:
            content = validateNotification(context, notification)
        except NotificationValueError:
            storage.removeNotification(notification)
            continue
        if IBrowserView.providedBy(content):
            url = content.context.absolute_url() + '/@@' + content.__name__
        else:
            context_state = content.restrictedTraverse('plone_context_state')
            url = context_state.view_url()

        title = show(content, request, notification)
        notifications.append({
            'title': title,
            'url': _redirectUrl(context, request, url, notification.where),
            'seen': notification.seen
        })
    storage.terminate()
    return notifications


def _redirectUrl(context, request, url, path):
    context = context.aq_inner
    portal_state = getMultiAdapter((context, request),
                                   name=u'plone_portal_state')
    base = portal_state.navigation_root().absolute_url()
    url = urllib.quote(url)
    path = urllib.quote(path)
    redirect = '%s/collective_whathappened_redirect?redirect=%s&path=%s'
    redirect = redirect % (base, url, path)
    return redirect


def _updateNotifications(context, storage, gatherer):
    lastCheck = _getLastCheck(context, storage)
    newNotifications = gatherer.getNewNotifications(lastCheck)
    if newNotifications is not None:
        for notification in newNotifications:
            storage.storeNotification(notification)


def _getPortalPath(context, request):
    context = context.aq_inner
    portal_state = getMultiAdapter((context, request),
                                   name=u'plone_portal_state')
    path = portal_state.navigation_root().getPhysicalPath()
    return '/'.join(path)


def _getLastCheck(context, storage):
    sdm = getToolByName(context, 'session_data_manager')
    session = sdm.getSessionData()
    if session is None or not SESSION_LAST_CHECK in session.keys():
        lastCheck = storage.getLastNotificationTime()
    else:
        lastCheck = session[SESSION_LAST_CHECK]
    session[SESSION_LAST_CHECK] = datetime.datetime.now()
    return lastCheck
