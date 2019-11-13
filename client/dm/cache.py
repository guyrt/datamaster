import os
import sqlite3
import uuid
import datetime

from .models import DataSet, DataSetFact, db, models_list
from .settings import local_datafile


class DataSetNotFoundError(Exception):
    pass

class TooManyDataSetsFoundError(Exception):
    pass


class DataMasterCache(object):

    def __init__(self):
        super(DataMasterCache, self).__init__()

    def get_datasets(self, active_only=True):
        return DataSet.select().where(DataSet.is_default==True)

    def get_dataset_byname(self, name):
        return DataSet.get(DataSet.name == name)

    def get_or_create_dataset(self, name, path, project, state, calling_filename, meta_args):
        # need to prehash the metaargs.
        metaarg_guid = DataSet.hash_metaarg(meta_args)
        dataset, created = DataSet.get_or_create(
            name=name, 
            project=project, 
            metaarg_guid=metaarg_guid, 
            defaults={'guid': uuid.uuid4()}
        )

        params_to_update = {'calling_filename': calling_filename, 'localpath': path, 'state': state}
        self._set_facts(dataset, params_to_update)

        if meta_args:
            # Meta args setting causes a file save.
            dataset.metaargs = meta_args
            
        dataset.last_modified_time = datetime.datetime.now()
        dataset.save()

        return dataset  # Todo verify this thing has the facts set up.

    def set_as_default(self, dataset):
        """ Set default to true for this data set, and default to false for all others """
        q = DataSet.update({DataSet.is_default: False}).where(DataSet.project == dataset.project and DataSet.name == dataset.name)
        q.execute()
        q = DataSet.update({DataSet.is_default: True}).where(DataSet.id == dataset.id)
        q.execute()

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
    db.create_tables(models_list)

cache = DataMasterCache()
