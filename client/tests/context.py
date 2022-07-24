import os
import shutil

import dm
import unittest
from peewee import SqliteDatabase
from dm.models import db, bootstrap_database


dm.settings.fileroot = "/tmp/datamastertest/"
dm.settings.metadata_fileroot = os.path.join(dm.settings.fileroot, '_metadata')
dm.settings.codecopy_fileroot = os.path.join(dm.settings.fileroot, '_codecopy')

class DMTestBase(unittest.TestCase):
    
    def setUp(self):
        # Create and clear file
        db.initialize(SqliteDatabase(":memory:"))
        bootstrap_database(db)

    def tearDown(self):
        shutil.rmtree(dm.settings.fileroot, onerror=lambda function, path, excinfo: print("Failed to delete {0}".format(path)))
