import os
import shutil
import mock

import dm
import unittest
from peewee import SqliteDatabase
from dm.settings import default_branch
from dm.models import db, bootstrap_database


class DMTestBase(unittest.TestCase):
    
    def setUp(self):
        dm.settings.save = mock.MagicMock()

        dm.settings.fileroot = "/tmp/datamastertest/"
        dm.settings.metadata_fileroot = os.path.join(dm.settings.fileroot, '_metadata')
        dm.settings.codecopy_fileroot = os.path.join(dm.settings.fileroot, '_codecopy')
        dm.settings.active_branch = default_branch  # always start here.
        db.initialize(SqliteDatabase(":memory:"))
        bootstrap_database(db)

    def tearDown(self):
        shutil.rmtree(dm.settings.fileroot, onerror=lambda function, path, excinfo: print("Failed to delete {0}".format(path)))
