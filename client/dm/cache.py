import hashlib
import os
import uuid
import datetime


from peewee import DoesNotExist, fn, SqliteDatabase

from .filetools import copy_file
from .models import (
    Branch,
    DataSet,
    DataSetFact, 
    db, 
    DatasetStates, 
    ModelConstants, 
    DataSetFactKeys,
    bootstrap_database
)
from .settings import settings
from .syncing import create_stale_syncs


class DataSetNotFoundError(Exception):
    pass


class TooManyDataSetsFoundError(Exception):
    pass


class DataSetNameCollision(Exception):
    pass


class DataMasterCache(object):

    def __init__(self):
        super(DataMasterCache, self).__init__()

    def get_or_create_branch(self, name):
        return Branch.get_or_create(name=name)[0]

    def get_datasets(self, active_only=True):
        active_branch = settings.active_branch
        return DataSet.select().where(DataSet.is_default==True and DataSet.branch==active_branch)

    def get_dataset_byname(self, name):
        return DataSet.get(DataSet.name == name)

    def get_dataset_by_args(self, dataset, file_extension, meta_args, timepath):
        """ Look up a dataset in same family but with a different file extension and/or metaargs 
        Should maintain branch of the dataset.
        """
        meta_args = self._combine_args(meta_args, file_extension)
        metaarg_guid = DataSet.hash_metaarg(meta_args)
        try:
            return DataSet.get(name=dataset.name, project=dataset.project, timepath=timepath, metaarg_guid=metaarg_guid, branch=dataset.branch)
        except DoesNotExist:
            return None

    def get_dataset_by_kwargs(self, name, project, branch, timepath, metaargs_guid, **kwargs):
        """
        Convenience function to find a dataset based on kwargs.

        kwargs are not used, but allow calling from json representation of a dataset.
        """
        try:
            return DataSet.get(
                name=name,
                project=project,
                branch=branch,
                timepath=timepath,
                metaarg_guid=metaargs_guid)
        except DoesNotExist:
            return None

    def get_or_create_dataset(self, name, path, metadata_path, project, timepath, file_extension, meta_args):
        timepath = timepath or ''  # convert null to string empty.
        meta_args = self._combine_args(meta_args, file_extension)

        # need to prehash the metaargs.
        metaarg_guid = DataSet.hash_metaarg(meta_args)
        with db.atomic():
            dataset, _ = DataSet.get_or_create(
                name=name,
                project=project,
                metaarg_guid=metaarg_guid,
                timepath=timepath,
                branch=settings.active_branch,
                defaults={'guid': uuid.uuid4()}
            )

            params_to_update = {
                DataSetFactKeys.LocalPath: path, 
                DataSetFactKeys.State: DatasetStates.LocalDeclared
            }
            if file_extension:
                params_to_update[DataSetFactKeys.FileExtension] = file_extension

            params_to_purge = []

            if meta_args:
                params_to_update[DataSetFactKeys.MetaArgFileName] = metadata_path
            else:
                params_to_purge.append(DataSetFactKeys.MetaArgFileName)

            self._set_facts(dataset, params_to_update, params_to_purge)

            dataset.last_modified_time = datetime.datetime.now()
            dataset.save()

        if meta_args:
            dataset.update_metaargs(meta_args)

        create_stale_syncs(dataset)

        return dataset  # Todo verify this thing has the facts set up.

    def _combine_args(self, meta_args, file_extension):
        meta_args = meta_args or dict()
        if file_extension:
            meta_args[ModelConstants.FileFormat] = file_extension
        return meta_args

    def check_project_isnt_file(self, project_name):
        """ ensure that there isn't a file that shares name with this project """
        project_parts = project_name.split('.')
        project_subname = '.'.join(project_parts[:-1])
        if DataSet.select().where(DataSet.project == project_subname, DataSet.name == project_parts[-1]).count() > 0:
            raise DataSetNameCollision("{0} is a project and can't be used as a filename.".format(project_name))

    def set_as_default(self, dataset):
        """ Set default to true for this data set, and default to false for all others on branch. """
        q = DataSet.update({DataSet.is_default: False}).where(
            DataSet.project == dataset.project, DataSet.name == dataset.name, DataSet.branch == dataset.branch
        )
        q.execute()
        q = DataSet.update({DataSet.is_default: True}).where(DataSet.id == dataset.id)
        q.execute()

    def set_facts_for_dataset_from_path(self, filepath, facts):
        dsf = DataSetFact.get(DataSetFact.key == 'localpath', DataSetFact.value == filepath)
        if not dsf:
            raise DataSetNotFoundError(filepath)
        dataset = dsf.dataset
        self._set_facts(dataset, facts)

    def _set_facts(self, dataset, facts, params_to_purge=None):
        for k, v in facts.items():
            ds, created = DataSetFact.get_or_create(dataset=dataset, key=k, defaults={'value': v})
            if not created:
                ds.value = v
                ds.save()
        if params_to_purge:
            DataSetFact.delete().where(DataSetFact.dataset==dataset, DataSetFact.key.in_(params_to_purge)).execute()

    def _cache_creating_file(self, dataset, creating_filename, codecopy_filename):
        """Get a copy of the creating filename and store it as a DataSetFact"""
        if not creating_filename or creating_filename == settings.cmdline_filename:
            # remove the keys this function sets.
            self._set_facts(dataset, {}, [DataSetFactKeys.CodeCopyFilename, DataSetFactKeys.CallingFilenameContentHash])
            return

        creating_filename = os.path.abspath(creating_filename)
        copy_file(creating_filename, codecopy_filename)

        hasher = hashlib.md5()
        with open(codecopy_filename, 'rb') as afile:
            buf = afile.read()
            hasher.update(buf)
        file_hash = hasher.hexdigest()
        new_kwargs = {
            DataSetFactKeys.CodeCopyFilename: codecopy_filename,
            DataSetFactKeys.CallingFilenameContentHash: file_hash
        }
        self._set_facts(dataset, new_kwargs)
    

def get_timepaths_for_dataset(dataset, limit=10):
    '''Identify all time paths in a dataset. Returns all of them if there are 10 or less. Returns min/max/count if more than 10.'''
    all_paths = DataSet.select().where(DataSet.name==dataset.name, DataSet.project==dataset.project, DataSet.metaarg_guid==dataset.metaarg_guid)
    total_records = all_paths.count()
    if total_records < limit:
        timepaths = list(all_paths.order_by(DataSet.timepath).select(DataSet.timepath).tuples())
        timepaths = [t[0] for t in timepaths]
        return {'allpaths': timepaths}
    else:
        min_value, max_value = timepaths.select(fn.Min(DataSet.timepath), fn.Max(DataSet.timepath)).scalar(as_tuple=True)
        return {'cnt': total_records, 'min_value': min_value, 'max_value': max_value}


# runs on startup
file_exists = os.path.exists(settings.local_database)
db.initialize(SqliteDatabase(settings.local_database))

if not file_exists:
    bootstrap_database(db)

cache = DataMasterCache()
