import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import dm
import unittest
from peewee import SqliteDatabase
from dm.models import DataSet, DataSetFact, models_list, db

dm.settings.default_fileroot = ".datamastertest/"

class DMTestBase(unittest.TestCase):
    
    def setUp(self):
        # Create and clear file
        pass

    def tearDown(self):
        for model in models_list:
            model.delete().execute()


db.initialize(SqliteDatabase(":memory:"))
db.create_tables(models_list)
