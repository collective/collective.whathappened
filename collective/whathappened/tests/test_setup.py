import unittest2 as unittest

from zope import component
from zope.publisher.interfaces.browser import IBrowserRequest
from plone.app.customerize import registration
from plone.registry.interfaces import IRegistry

from collective.whathappened.tests import base
from collective.whathappened.gatherer_backend import IGathererBackend


class TestSetup(base.IntegrationTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def test_browserlayer(self):
        from plone.browserlayer import utils
        from collective.whathappened import layer
        self.assertIn(layer.Layer, utils.registered_layers())

    def test_storage(self):
        self.registry = component.queryUtility(IRegistry)
        self.assertIsNotNone(self.registry)
        backend = self.registry.get(
            'collective.whathappened.backend',
            'collective.whathappened.backend.sqlite',
        )
        self.backend = self.portal.restrictedTraverse(backend)
        self.assertIsNotNone(self.backend)

    def test_gatherer(self):
        views = registration.getViews(IBrowserRequest)
        self.backends = [
            view.factory(self.portal, self.request) for view in views
            if IGathererBackend.implementedBy(view.factory)
        ]
        self.assertEqual(len(self.backends), 1)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
