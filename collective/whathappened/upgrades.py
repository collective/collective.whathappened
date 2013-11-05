import os
import sqlite3

from Products.CMFCore.utils import getToolByName

from collective.whathappened import config

PROFILE = 'profile-collective.whathappened:default'


def common(context):
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile(PROFILE)


def upgrade_db(context):
    for file_name in os.listdir(config.sqlite_directory):
        if file_name.endswith('.sqlite'):
            try:
                db = sqlite3.connect('%s/%s' % (config.sqlite_directory,
                                                file_name))
                db.execute("""ALTER TABLE notifications ADD
                              `info` TEXT""")
                db.commit()
                db.close()
            except:
                pass
