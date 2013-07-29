from plone.app.contentrules.handlers import execute


def subscribed(event):
    obj = event.object
    execute(obj, event)


def blacklisted(event):
    obj = event.object
    execute(obj, event)
