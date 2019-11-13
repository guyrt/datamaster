import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import dm
import unittest
from peewee import SqliteDatabase
from dm.models import DataSet, DataSetFact, models_list
import dm

dm.settings.default_fileroot = ".datamastertest/"

class DMTestBase(unittest.TestCase):
    
    def setUp(self):
        # Create and clear file
        pass

    def tearDown(self):
        for model in models_list:
            model.delete().execute()


test_db = SqliteDatabase(":memory:")
test_db.bind(models_list)
test_db.create_tables(models_list)

