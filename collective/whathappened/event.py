from zope.component.interfaces import ObjectEvent
from zope import interface
from zope.component.interfaces import IObjectEvent


class ISubscribedEvent(IObjectEvent):
    pass


class SubscribedEvent(ObjectEvent):
    interface.implements(ISubscribedEvent)


class IBlacklistedEvent(IObjectEvent):
    pass


class BlacklistedEvent(ObjectEvent):
    interface.implements(IBlacklistedEvent)
