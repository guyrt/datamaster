import os
import sqlite3
import uuid

local_datafile = 'C:/users/riguy/.datamaster/dbmaster.db'


class DatasetStates(object):

    LocalDeclared = "localdeclared"
    LocalSaved = "localsaved"


class DataSet(object):

    def __init__(self, name, id = None, guid = None):
        super(DataSet, self).__init__()
        self.name = name
        self.id = id
        self.guid = guid


class DataSetFacts(object):

    def __init__(self, id, key, value):
        self.id = id
        self.key = key
        self.value = value

    def save(self, conn):
        conn.execute('''
        INSERT INTO {table}(id, key, value) VALUES ({id}, '{key}', '{value}')
        ON CONFLICT(id, key) DO UPDATE SET value='{value}'
        '''.format(table = 'datasetfacts', id=self.id, key=self.key, value=self.value))


class DataMasterCache(object):

    def __init__(self):
        super(DataMasterCache, self).__init__()

    def create_or_update_dataset(self, name, path, state):
        """ TODO: probably accept an object here

        If we don't have a data set, create one. If we do, then set its path.
        """
        conn = check_database()
        data_set = self._get_dataset(conn, name)
        if not data_set:
            data_set = self._create_dataset(conn, name)

        self._set_facts(data_set, conn, {'localpath': path, 'state': state})
        conn.commit()
        return data_set

    def get_datasets(self):
        conn = check_database()
        datasets = conn.execute("SELECT * FROM {datasets}".format(datasets='datasets'))
        return [DataSet(d[1], d[0], d[2]) for d in datasets]

    def _set_facts(self, data_set, conn, facts):
        for k, v in facts.items():
            DataSetFacts(data_set.id, k, v).save(conn)

    def _create_dataset(self, conn, name):
        guid = uuid.uuid4()
        conn.execute("INSERT INTO {datasets} (name, guid) VALUES ('{name}', '{guid}')".format(datasets='datasets', name=name, guid=guid))
        conn.commit()
        return self._get_dataset(conn, name)

    def _get_dataset(self, conn, name):
        data_id = conn.execute("SELECT * FROM {datasets} WHERE name = '{name}'".format(datasets='datasets', name=name)).fetchone()
        if data_id:
            return DataSet(data_id[1], data_id[0], data_id[2])
        return None


def check_database():
    if not os.path.exists(local_datafile):
        return create_database()
    return _get_db()

def create_database():
    print("Creating DataMaster database")
    conn = sqlite3.connect(local_datafile)
    conn.execute("CREATE TABLE datasets (id INTEGER PRIMARY KEY AUTOINCREMENT, name text UNIQUE, guid text)")
    conn.execute("CREATE TABLE datasetfacts (id int, key text, value text)")
    conn.execute("CREATE UNIQUE INDEX datasetfacts_id_key ON datasetfacts(id, key)")
    conn.commit()
    return conn

def _get_db():
    return sqlite3.connect(local_datafile)