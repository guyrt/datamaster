import os
import inspect
from .cache import DataMasterCache, DatasetStates

default_filesuffix = "txt"

# TODO look up in settings
default_fileroot = "C:/tmp/play/"

if not os.path.exists(default_fileroot):
    os.makedirs(default_fileroot)


cache = DataMasterCache()

class MaybeFileName(os.PathLike):

    def __init__(self, name):
        """
        """
        # TODO look up settings
        self._prefix = default_fileroot
        if type(name) == str:
            self._name = [name]
        else:
            self._name = name

    def __getattribute__(self, name):
        """Here, name is playing the role of a new suffix."""
        if name.startswith("_"):
            return super(MaybeFileName, self).__getattribute__(name)
        return MaybeFileName(self._name + [name])

    def _get_path(self):
        if len(self._name) > 1:
            filename = '.'.join(self._name)
            datasetname = '.'.join(self._name[:-1])
        else:
            filename = self._name[0] + "." + default_filesuffix
            datasetname = self._name[0]
        full_path = os.path.join(self._prefix, filename)
        return full_path, datasetname

    def __repr__(self):
        full_path, datasetname = self._get_path()
        return "DataSet: {dsn} local at {fp}".format(dsn=datasetname, fp=full_path)

    def __str__(self):
        full_path, _ = self._get_path()
        return full_path

    def __fspath__(self):
        print("Query FSPath")
        full_path, datasetname = self._get_path()
        # TODO - get the path portion and ensure that it exists.
        cache.create_or_update_dataset(datasetname, full_path, DatasetStates.LocalDeclared)
        return full_path


class DataMasterOutput(object):
    """
    Provide paths for writing data.

    TODO:
        handle file types? Can use dot notation or can use suffix or can use
        handle both attribute and function style, where function is for specifying stuff.
            this should enable saving in /2019/10/11/ for instance. Needs coordination with the MaybeFileName.
    """

    def __init__(self):
        super(DataMasterOutput, self).__init__()

    def __getattribute__(self, name):
        if name.startswith("_"):
            return super(DataMasterOutput, self).__getattribute__(name)
        print(f"You requested file {name}")
        return MaybeFileName(name)


class DataMasterInput(object):
    """
    Provide paths for reading existing data.

    TODO:
        support a path that wraps an existing data file. then it becomes a data file.
    """

    def __init__(self):
        super(DataMasterInput, self).__init__()
        
        cache = DataMasterCache()
        for dataset in cache.get_datasets():
            setattr(self, dataset.name, dataset.name)  # todo get path

    def __getattribute__(self, name):
        if name.startswith("_"):
            return super(DataMasterInput, self).__getattribute__(name)
        return MaybeFileName(name)


"""

open(out.txt.dataset)  <--- format.name
open(out.dataset.txt)  <--- name.format [feels more natural i think]
open(out.dataset)      <--- gives just a name. no suffix at all. or .dat?

open(in.dataset.txt)   <--- works.
open(in.dataset)       <--- will give the default dataset type.
open(in.dataset.parquet)  <--- looking for a parquet format of that dataset.

Then support transformers (built-in pipeline units) to convert formats.

"""

"""
localframe = inspect.currentframe().f_back   <--- gets you who called.
"""

