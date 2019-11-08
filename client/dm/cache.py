import os
import sqlite3
import uuid
from peewee import Model, CharField, ForeignKeyField, SqliteDatabase

local_datafile = 'C:/users/riguy/.datamaster/dbmaster.db'
db = SqliteDatabase(local_datafile)

class DataSetNotFoundError(Exception):
    pass

class TooManyDataSetsFoundError(Exception):
    pass


class DatasetStates(object):

    LocalDeclared = "localdeclared"
    LocalSaved = "localsaved"

class DataSet(Model):

    name = CharField(max_length=512)
    project = CharField(max_length=512)
    guid = CharField(max_length=64, unique=True)

    class Meta:
        database = db
        indexes = (
            (('name', 'project'), True),
        )

class DataSetFact(Model):

    dataset = ForeignKeyField(DataSet, backref='facts')
    key = CharField()
    value = CharField()

    class Meta:
        database = db
        indexes = (
            (('dataset', 'key'), True),
        )


class DataMasterCache(object):

    def __init__(self):
        super(DataMasterCache, self).__init__()

    def get_datasets(self):
        return DataSet.select()

    def get_dataset_byname(self, name):
        return DataSet.get(DataSet.name == name)

    def get_or_create_dataset(self, name, path, project, state, calling_filename):
        dataset, created = DataSet.get_or_create(name=name, project=project, defaults={'guid': uuid.uuid4()})
        params_to_update = {'calling_filename': calling_filename, 'localpath': path, 'state': state}
        self._set_facts(dataset, params_to_update)
        
        return dataset  # Todo verify this thing has the facts set up.

    def set_facts_for_dataset_from_path(self, filepath, facts):
        dsf = DataSetFact.get(DataSetFact.key == 'localpath', DataSetFact.value == filepath)
        if not dsf:
            raise DataSetNotFoundError(filepath)
        dataset = dsf.dataset
        self._set_facts(dataset, facts)

    def _set_facts(self, dataset, facts):
        for k, v in facts.items():
            ds, created = DataSetFact.get_or_create(dataset=dataset, key=k, defaults={'value': v})
            if not created:
                ds.value = v
                ds.save()

# runs on startup

file_exists = os.path.exists(local_datafile)
db.connect()
if not file_exists:
    db.create_tables([DataSet, DataSetFact])