import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import dm
import unittest
from peewee import SqliteDatabase
from dm.models import DataSet, DataSetFact, Branch, models_list, db, bootstrap_database
from dm.settings import default_branch


dm.settings.fileroot = "/tmp/datamastertest/"
dm.settings.metadata_fileroot = os.path.join(dm.settings.fileroot, '_metadata')

class DMTestBase(unittest.TestCase):
    
    def setUp(self):
        # Create and clear file
        pass

    def tearDown(self):
        for model in models_list:
            model.delete().execute()
        Branch.create(name=default_branch)


db.initialize(SqliteDatabase(":memory:"))
bootstrap_database(db)
