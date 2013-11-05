from plone.autoform import directives
from plone.autoform.form import AutoExtensibleForm
from plone.z3cform.layout import FormWrapper
from z3c.form import form
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import component
from zope import interface
from zope import schema

from collective.whathappened.i18n import _
from collective.whathappened.storage_manager import StorageManager


class ManageFormSchema(interface.Interface):
    directives.widget('subscriptions', CheckBoxFieldWidget)
    subscriptions = schema.List(
        title=u"Subscriptions",
        value_type=schema.Choice(
            vocabulary="collective.whathappened.vocabularies.subscriptions"
        )
    )


class ManageFormAdapter(object):
    component.adapts(interface.Interface)
    interface.implements(ManageFormSchema)

    def __init__(self, context):
        self.context = context


class ManageForm(AutoExtensibleForm, form.Form):
    schema = ManageFormSchema
    enableCSRFProtection = True
    label = _("Manage my subscriptions")

    def updateWidgets(self):
        super(ManageForm, self).updateWidgets()
        for item in self.widgets['subscriptions'].items:
            item['checked'] = True

    @button.buttonAndHandler(_(u"Save"))
    def handleManage(self, action):
        data, errors = self.extractData()
        if errors:
            return
        storage = StorageManager(self.context)
        storage.initialize()
        subscriptions = storage.getSubscriptions()
        for s in subscriptions:
            if s.where not in data['subscriptions']:
                s.wants = None
                storage.saveSubscription(s)
        storage.terminate()
        self.request.response.redirect('@@collective_whathappened_manage')


class ManageFormWrapper(FormWrapper):
    form = ManageForm
    label = _("Manage my subscriptions")
