from plone.app.registry.browser import controlpanel
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from zope import component

from collective.whathappened.i18n import _
from collective.whathappened.settings import ISettings


class SettingsEditForm(controlpanel.RegistryEditForm):
    schema = ISettings
    label = _("Whathappened settings")


class SettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = SettingsEditForm


class getSettings(BrowserView):
    def __call__(self):
        registry = component.getUtility(IRegistry)
        settings = registry.forInterface(ISettings)
        return settings
