from zope.i18n import translate
from zope import interface

from collective.history.i18n import _ as _h
from collective.whathappened.i18n import _


class IDisplay(interface.Interface):
    """Marker interface for class displaying a notification.
    Name of the utility must be the msgid of the what."""

    def display(context, request, notification):
        """Return a ready to display string for the given notification."""


class DefaultDisplay(object):
    interface.implements(IDisplay)

    def display(self, context, request, notification):
        self.what = translate(_h(notification.what.decode("utf-8")),
                         domain="collective.history", context=request)
        where = notification.where.encode('utf-8')
        try:
            title = context.restrictedTraverse(where).Title()
            self.where = title.decode('utf-8')
        except KeyError:
            self.where = where.split('/')[-1]
        self.who = ', '.join(notification.who)
        self.plural = True if len(notification.who) > 1 else False
        if self.plural:
            _(u"${who} have ${what} ${where}",
                     mapping={'who': self.who,
                              'what': self.what,
                              'where': self.where
                              })
        else:
            return _(u"${who} has ${what} ${where}",
                     mapping={'who': self.who,
                              'what': self.what,
                              'where': self.where
                              })
