from zope import interface
from zope import schema

from collective.whathappened.i18n import _


class ISettings(interface.Interface):

    useraction_gatherer_whitelist = schema.Set(
        title=_(u"Useraction gatherer whitelist"),
        description=_(u"Only the useraction with these 'what' will be stored."
                      u" One what per line."),
        value_type=schema.TextLine(),
    )
