from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from collective.whathappened.i18n import _

subscriptionChoice = SimpleVocabulary([
    SimpleTerm('subscribe', 'subscribe', _(u'Subscribe')),
    SimpleTerm('unsubscribe', 'unsubscribe', _(u'Unsubscribe')),
])
