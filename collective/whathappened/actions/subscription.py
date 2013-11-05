import sqlite3

from OFS.SimpleItem import SimpleItem
from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.contentrules.rule.interfaces import IRuleElementData, IExecutable
from Products.CMFPlone import PloneMessageFactory as _p
from zope.formlib import form
from zope.component import adapts
from zope import interface
from zope import schema

from collective.whathappened.actions.vocabularies import subscriptionChoice
from collective.whathappened.i18n import _
from collective.whathappened.storage_manager import StorageManager
from collective.whathappened.subscription import Subscription


class ISubscriptionAction(interface.Interface):
    """Definition of the configuration available for a subscription action."""

    subscription = schema.Choice(
        title=_(u"Change subscription"),
        vocabulary=subscriptionChoice
    )


class SubscriptionAction(SimpleItem):
    interface.implements(ISubscriptionAction, IRuleElementData)

    subscription = 'subscribe'
    element = 'collective.whathappened.actions.Subscription'
    summary = _(u'Change the user\'s subscription to this object.')


class SubscriptionActionExecutor(object):
    interface.implements(IExecutable)
    adapts(interface.Interface, ISubscriptionAction, interface.Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        subscription = self.element.subscription
        obj = self.event.object
        storage = StorageManager(self.context)
        context_path = '/'.join(obj.getPhysicalPath())
        try:
            storage.initialize()
            if subscription == 'subscribe':
                storage.saveSubscription(
                    Subscription(context_path, True)
                )
            else:
                storage.saveSubscription(
                    Subscription(context_path, False)
                )
            storage.terminate()
        except sqlite3.IntegrityError:
            return False
        return True


class SubscriptionActionAddForm(AddForm):
    form_fields = form.FormFields(ISubscriptionAction)
    label = _(u'Add subscription action')
    description = _(u'An action which can add or remove the subscription '
                    u'to an object')
    form_name = _p(u'Configure element')

    def create(self, data):
        a = SubscriptionAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class SubscriptionActionEditForm(EditForm):
    form_fields = form.FormFields(ISubscriptionAction)
    label = _(u'Edit subscription action')
    description = _(u'An action which can add or remove the subscription '
                    u'to an object')
    form_name = _p(u'Configure element')
