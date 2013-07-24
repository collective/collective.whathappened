from zope.component.interfaces import ObjectEvent
from zope import interface
from zope.component.interfaces import IObjectEvent

class ISubscribedEvent(IObjectEvent):
    pass


class SubscribedEvent(ObjectEvent):
    interface.implements(ISubscribedEvent)


class IUnsubscribedEvent(IObjectEvent):
    pass


class UnsubscribedEvent(ObjectEvent):
    interface.implements(IUnsubscribedEvent)
