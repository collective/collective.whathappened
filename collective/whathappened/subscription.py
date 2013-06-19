from zope import interface
from zope import schema

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

class ISubscription(interface.Interface):
    """A subscription represents a specific location the user
    wants to be notified about or not"""

    where = schema.ASCIILine(title=u"Where")
    wants = schema.Bool(title=u"wants")


class Subscription(object):
    interface.implements(ISubscription)

    def __init__(self, where, wants):
        self.where = where
        self.wants = wants
