from peewee import Model, CharField, ForeignKeyField, IntegerField, SqliteDatabase, TextField, DoesNotExist, DateTimeField
import json
import os
import hashlib
import datetime

from .setting import default_fileroot, local_datafile

db = SqliteDatabase(local_datafile)


class DatasetStates(object):

    LocalDeclared = "localdeclared"
    LocalSaved = "localsaved"


class DataSet(Model):

    name = CharField(max_length=512)
    project = CharField(max_length=512)
    guid = CharField(max_length=64, unique=True)
    metaarg_guid = CharField(max_length=64)
    last_modified_time = DateTimeField(default=datetime.datetime.now)
    
    def __repr__(self):
        return "DataSet {id} {project}.{name}".format(id=self.id, project=self.project, name=self.name)

    # Holds a json representation of arguments associated with this version.
    def __init__(self, *args, **kwargs):
        super(DataSet, self).__init__(*args, **kwargs)
        self._metaargs = dict()

    @property
    def metaargs(self):
        return self._metaargs

    @metaargs.setter
    def metaargs(self, metaargs):
        self._metaargs = metaargs
        self.metaarg_guid = self.hash_metaarg(self._metaargs)

    def save(self, *args, **kwargs):
        """ Save then dump metaargs nearby. """
        super(DataSet, self).save(*args, **kwargs)
        _dump_metaargs(self)

    def get_local_filename(self):
        try:
            return DataSetFact.get(dataset=self, key='localpath').value
        except DoesNotExist:
            return None

    @staticmethod
    def hash_metaarg(metaargs):
        if metaargs:
            return hashlib.md5(repr(sorted(metaargs.items())).encode('utf-8')).hexdigest()
        else:
            return ''

    class Meta:
        database = db
        indexes = (
            (('name', 'project', 'metaarg_guid'), True),
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


def _dump_metaargs(dataset):
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
