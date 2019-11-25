from peewee import Model, CharField, ForeignKeyField, IntegerField, SqliteDatabase, TextField, DoesNotExist, DateTimeField, BooleanField
import json
import os
import hashlib
import datetime
import warnings

from .settings import default_fileroot, local_datafile

db = SqliteDatabase(local_datafile)


class DatasetStates(object):

    LocalDeclared = "localdeclared"
    LocalSaved = "localsaved"


class ModelConstants(object):

    # Stored in metaargs b/c it forms part of file uniqueness, 
    # used to store file format.
    FileFormat = 'extension'


class DataSet(Model):

    name = CharField(max_length=512)
    project = CharField(max_length=512)
    guid = CharField(max_length=64, unique=True)
    metaarg_guid = CharField(max_length=64)
    timepath = CharField(max_length=64, default='')
    last_modified_time = DateTimeField(default=datetime.datetime.now)
    is_default = BooleanField(default=True)

    class Meta:
        database = db
        indexes = (
            (('name', 'project', 'metaarg_guid', 'timepath'), True),
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

    def update_metaargs(self, metaargs):
        self._metaargs.update(metaargs)
        self.metaarg_guid = self.hash_metaarg(self._metaargs)

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
        return self.get_fact('localpath')

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
        metaarg_file = self.get_fact('metaargfilename')
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


models_list = (DataSet, DataSetFact)


def _dump_metaargs(dataset):
    if not dataset.metaargs:
        return
    metaargs_str = json.dumps(dataset.metaargs)
    data_filename = dataset.get_local_filename()
    if not data_filename:
        return
    dump_filename = data_filename + "." + dataset.metaarg_guid
    f = open(dump_filename, 'w')
    f.write(metaargs_str)
    f.close()
    dsf, created = DataSetFact.get_or_create(dataset=dataset, key='metaargfilename', defaults={'value': dump_filename})
    if not created:
        dsf.value = dump_filename
        dsf.save()
    return dsf
