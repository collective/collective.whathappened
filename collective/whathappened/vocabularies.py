from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from collective.whathappened.i18n import _
from collective.whathappened.storage_manager import StorageManager


def _getTitle(context, subscription):
    content = context.restrictedTraverse(subscription.where.encode('utf-8'))
    if subscription.wants:
        return content.title
    else:
        return _(u'${title} (blacklisted)',
                 mapping={
                'title': content.title
                })


def subscriptions(context):
    storage = StorageManager(context)
    storage.initialize()
    subscriptions = storage.getSubscriptions()
    storage.terminate()
    terms = [
        SimpleTerm(
            s.where,
            s.where,
            _getTitle(context, s)
            ) for s in subscriptions
        ]
    return SimpleVocabulary(terms)
