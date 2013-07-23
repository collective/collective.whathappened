from zope.component.interfaces import ObjectEvent
from zope import event


class ISubscribedEvent(interface.Interface):
    pass


class SubscribedEvent(ObjectEvent):
    interface.Implements(ISubscribedEvent)


class IUnsubscribedEvent(interface.Interface):
    pass


class UnsubscribedEvent(ObjectEvent):
    interface.Implements(IUnsubscribedEvent)
