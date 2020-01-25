from peewee import Model, CharField, ForeignKeyField, IntegerField, TextField, DoesNotExist, DateTimeField, BooleanField
from peewee import DatabaseProxy
import json
import os
import hashlib
import datetime
import warnings

from .filetools import make_folder
from .settings import default_branch

db = DatabaseProxy()

class DatasetStates(object):

    LocalDeclared = "localdeclared"
    LocalSaved = "localsaved"


class ModelConstants(object):

    # Stored in metaargs b/c it forms part of file uniqueness, 
    # used to store file format.
    FileFormat = 'extension'


class DataSetFactKeys(object):
    """
    Allowable fields for the key field in DataSetFact
    """

    CallingFilename = 'calling_filename'
    CallingFilenameContentHash = 'calling_filename_content_hash'
    CodeCopyFilename = 'code_copy_filename'
    LocalPath = 'localpath'
    State = 'state'
    LocalMachine = 'localmachine'
    LocalUsername = 'localusername'
    MetaArgFileName = 'metaargfilename'
    PreviousFileReads = 'previousfilereads'

    # Git facts
    GitRoot = 'git_root'
    GitActiveBranch = 'git_active_branch'
    GitCommitHexSha = 'git_commit_hexsha'
    GitCommitAuthor = 'git_commit_author'
    GitCommitAuthoredDatetime = 'git_commit_authored_datetime'

    # Not stored in DB locally - used to send to server
    CodeCopyContent = 'code_copy_contents'


class BranchSyncableState(object):

    Sync = "sync"
    LocalOnly = "localonly"


class Branch(Model):
    """ Track metadata information about a branch. Generally, git's structure should rule here. 
    
    While we store the fact that a branch exists here, the active branch for a context is stored
    in a file in the context root.
    """

    name = CharField(primary_key=True, max_length=256)
    syncable_state = CharField(default=BranchSyncableState.LocalOnly)

    class Meta:
        database = db


class DataSet(Model):
    """
    Main storage module for a data file or folder created by a user.
    """

    name = CharField(max_length=512)
    project = CharField(max_length=512)
    metaarg_guid = CharField(max_length=64)
    timepath = CharField(max_length=64, default='')
    branch = ForeignKeyField(Branch, backref='datasets', field='name')

    guid = CharField(max_length=64, unique=True)
    last_modified_time = DateTimeField(default=datetime.datetime.now)
    is_default = BooleanField(default=True)

    class Meta:
        database = db
        indexes = (
            # Note the 4-part primary key for this object.
            (('branch', "project", 'name', 'metaarg_guid', 'timepath'), True),
        )

    def __repr__(self):
        return "DataSet {id} {project}.{name}".format(id=self.id, project=self.project, name=self.name)

    # Holds a json representation of arguments associated with this version.
    def __init__(self, *args, **kwargs):
        super(DataSet, self).__init__(*args, **kwargs)
        self._metaargs = dict()

    @property
    def full_name(self):
        if self.project:
            return self.project + '.' + self.name
        return self.name

    @property
    def metaargs(self):
        return self._metaargs

    def update_metaargs(self, metaargs, metadata_path=None):
        self._metaargs.update(metaargs)
        self.metaarg_guid = self.hash_metaarg(self._metaargs)
        if metadata_path:
            _dump_metaargs(self, metadata_path)

    def save(self, *args, **kwargs):
        """ Save then dump metaargs nearby. """
        super(DataSet, self).save(*args, **kwargs)
        _dump_metaargs(self)

    def get_fact(self, key):
        try:
            return DataSetFact.get(dataset=self, key=key).value
        except DoesNotExist:
            return None

    def get_local_filename(self):
        return self.get_fact(DataSetFactKeys.LocalPath)

    def get_metadata_filename(self):
        return self.get_fact(DataSetFactKeys.MetaArgFileName)

    def get_local_machine_name(self):
        return self.get_fact(DataSetFactKeys.LocalMachine)

    def load_metaargs(self):
        """If metargs are empty then try to reload from DB."""
        if self.metaargs:
            return self.metaargs
        s = self.get_metaargs_str()
        if not s:
            return self.metaargs
        metaargs_local = json.loads(s)
        self.update_metaargs(metaargs_local)
        return self.metaargs

    def get_metaargs_str(self, charlimit=None):
        """ Just get the string metaargs. Does not resolve them. """
        metaarg_file = self.get_fact(DataSetFactKeys.MetaArgFileName)
        if not metaarg_file:
            return None
        try:
            f = open(metaarg_file, 'r')
        except FileNotFoundError:
            warnings.warn('Metadata file not found for: {0}'.format(self.name), UserWarning)
            return None
        if charlimit:
            txt = f.read(charlimit)
        else:
            txt = f.read()
        f.close()
        return txt

    @staticmethod
    def hash_metaarg(metaargs):
        if metaargs:
            return hashlib.md5(repr(sorted(metaargs.items())).encode('utf-8')).hexdigest()
        else:
            return ''


class DataSetFact(Model):

    dataset = ForeignKeyField(DataSet, backref='facts')
    key = CharField()
    value = CharField()

    def __repr__(self):
        return "DataSetFact {dataset} {key} -> {value}".format(dataset=self.dataset.id, key=self.key, value=self.value)

    class Meta:
        database = db
        indexes = (
            (('dataset', 'key'), True),
        )


class DataSetRemoteSyncStates(object):

    Stale = 'stale'  # Need to sync this.
    Synced = 'synced'  # Latest change was pushed to server.


class DataSetRemoteSync(Model):
    """Track remote sync states"""

    dataset = ForeignKeyField(DataSet, backref='serversyncs')
    remote = CharField(default='main')  # name of the remote. For now, we only support one.
    sync_state = CharField(default=DataSetRemoteSyncStates.Stale)  # state of this sync.

    class Meta:
        database = db
        indexes = (
            (('dataset', 'remote'), True),
        )


models_list = (DataSet, DataSetFact, DataSetRemoteSync, Branch)


def _dump_metaargs(dataset, dump_filename=None):
    if not dataset.metaargs:
        return
    metaargs_str = json.dumps(dataset.metaargs)
    if not dump_filename:
        dump_filename = dataset.get_metadata_filename()
    make_folder(dump_filename)
    f = open(dump_filename, 'w')
    f.write(metaargs_str)
    f.close()
    dsf, created = DataSetFact.get_or_create(dataset=dataset, key=DataSetFactKeys.MetaArgFileName, defaults={'value': dump_filename})
    if not created:
        dsf.value = dump_filename
        dsf.save()
    return dsf


def bootstrap_database(db_instance):
    db_instance.create_tables(models_list)
    Branch.create(name=default_branch)
