from zope import interface
from zope import schema


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
