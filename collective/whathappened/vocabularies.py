from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from collective.whathappened.i18n import _
from collective.whathappened.storage_manager import StorageManager
from AccessControl.unauthorized import Unauthorized


def _getTitle(context, subscription):
    try:
        content = context.restrictedTraverse(subscription.where.encode('utf-8'))
    except Unauthorized:
        return
    except KeyError:
        return
    if subscription.wants:
        return content.title
    else:
        return _(u'${title} (blacklisted)',
                 mapping={'title': content.title})


def subscriptions(context):
    storage = StorageManager(context)
    storage.initialize()
    subscriptions = storage.getSubscriptions()
    storage.terminate()
    terms = []
    for s in subscriptions:
        title = _getTitle(context, s)
        if title is None:
            #TODO: delete subscription
            continue
        terms.append(SimpleTerm(s.where, s.where, title))
    return SimpleVocabulary(terms)
