from AccessControl.unauthorized import Unauthorized

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

from collective.whathappened.storage_manager import StorageManager


class RedirectView(BrowserView):
    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        user = mtool.getAuthenticatedMember().getId()
        if user is None:
            raise Unauthorized

        redirect = self.request.get('redirect', None)
        path = self.request.get('path', None)
        if redirect is None or path is None:
            return
        storage = StorageManager(self.context, self.request)
        storage.initialize()
        storage.setSeen(path)
        storage.terminate()
        self.request.response.redirect(redirect)
