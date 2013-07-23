from zope.component.interfaces import ObjectEvent
from zope import interface


class ISubscribedEvent(interface.Interface):
    pass


class SubscribedEvent(ObjectEvent):
    interface.implements(ISubscribedEvent)


class IUnsubscribedEvent(interface.Interface):
    pass


class UnsubscribedEvent(ObjectEvent):
    interface.implements(IUnsubscribedEvent)
