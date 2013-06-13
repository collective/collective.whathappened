from plone.app.testing import *
import collective.whathappened


FIXTURE = PloneWithPackageLayer(
    zcml_filename="configure.zcml",
    zcml_package=collective.whathappened,
    additional_z2_products=[],
    gs_profile_id='collective.whathappened:default',
    name="collective.whathappened:FIXTURE"
)

INTEGRATION = IntegrationTesting(
    bases=(FIXTURE,), name="collective.whathappened:Integration"
)

FUNCTIONAL = FunctionalTesting(
    bases=(FIXTURE,), name="collective.whathappened:Functional"
)
