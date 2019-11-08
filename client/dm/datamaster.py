import os
import inspect
import git
from .cache import DataMasterCache, DatasetStates

default_filesuffix = "txt"

# TODO look up in settings
default_fileroot = "C:/tmp/play/"

if not os.path.exists(default_fileroot):
    os.makedirs(default_fileroot)


cache = DataMasterCache()


class ReadableFileName(os.PathLike):

    pass


class WriteableFileName(os.PathLike):
    """todo: class docstring"""

    def __init__(self, name, calling_filename):
        # TODO look up settings
        self._prefix = default_fileroot
        self._calling_filename = calling_filename
        self._default_filesuffix = None
        if type(name) == str:
            self._name = [name]
        else:
            self._name = name

    def __call__(self, filetype):
        self._default_filesuffix = filetype
        return self

    def __getattribute__(self, name):
        """Here, name is playing the role of a new suffix."""
        if name.startswith("_"):
            return super(WriteableFileName, self).__getattribute__(name)
        return WriteableFileName(self._name + [name], self._calling_filename)

    def _get_path(self):
        filename = self._name[-1]
        if self._default_filesuffix:
            filename += "." + self._default_filesuffix
        datasetname = self._name[-1]
        project = '.'.join(self._name[:-1])
        full_path = os.path.join(self._prefix, os.path.join(project), filename)
        return full_path, datasetname, project

    def __repr__(self):
        full_path, datasetname, project = self._get_path()
        return "DataSet: {project}.{dsn} local at {fp}".format(project=project, dsn=datasetname, fp=full_path)

    def __str__(self):
        full_path, _, _ = self._get_path()
        return full_path

    def __fspath__(self):
        full_path, datasetname, project = self._get_path()
        path_part = os.path.dirname(full_path)
        if not os.path.exists(path_part):
            os.makedirs(path_part)
        # TODO: pass project into create/update.
        cache.get_or_create_dataset(datasetname, full_path, project, DatasetStates.LocalDeclared, self._calling_filename)
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
        iframe = inspect.currentframe().f_back
        calling_filename = _get_clean_filename(iframe)
        return WriteableFileName(name, calling_filename)


class DataMasterInput(object):
    """
    Provide paths for reading existing data.

    TODO:
        support a feature that wraps an existing data file. then it becomes a data file. Basically, delegate this to the output stuff.
    """

    def __init__(self):
        super(DataMasterInput, self).__init__()
        
        cache = DataMasterCache()
        for dataset in cache.get_datasets():
            setattr(self, dataset.name, WriteableFileName(dataset.name, None))  # todo get path


def _get_clean_filename(iframe):
    rawpath = iframe.f_code.co_filename
    full_path = os.path.abspath(rawpath)
    try:
        git_repo = git.Repo(full_path, search_parent_directories=True)
    except git.NoSuchPathError:
        return full_path
    git_root = git_repo.git.rev_parse("--show-toplevel")
    if git_root:
        git_root_path = len(str(git_root)) + 1
        final_path = full_path[git_root_path:]
    else:
        final_path = full_path
    return os.path.basename(final_path)

"""
open(out.project.dataset.txt)   <---- allow for project. But what about 2? assume no project i think.

open(in.dataset.txt)   <--- works.
open(in.dataset)       <--- will give the default dataset type.
open(in.dataset.parquet)  <--- looking for a parquet format of that dataset. Then support transformers (built-in pipeline units) to convert formats.
"""
