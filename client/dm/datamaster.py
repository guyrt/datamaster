import git
import inspect
import os

from .cache import cache
from .models import DatasetStates, DataSet
from .settings import default_fileroot
from .readablefile import inputs


class WriteableFileName(os.PathLike):
    """todo: class docstring"""

    def __init__(self, name, calling_filename):
        self._prefix = default_fileroot
        self._filesuffix = None
        self._metaargs = {}  # These can be used to version.
        self._is_project = False  # True iff this is not a file.

        if type(name) == str:
            self._name = [name]
        else:
            self._name = name

        self._calling_filename = calling_filename

    def __call__(self, format=None, meta=None):
        if format:
            self._filesuffix = format
        if meta:
            self._metaargs = meta
        return self

    def _set_internal_attributes(self, parent):
        self._filesuffix = parent._filesuffix
        self._metaargs = parent._metaargs

    def __getattribute__(self, name):
        """Here, name is playing the role of a new suffix."""
        if name.startswith("_"):
            return super(WriteableFileName, self).__getattribute__(name)
        new_writeable = WriteableFileName(self._name + [name], self._calling_filename)
        new_writeable._set_internal_attributes(self)
        self._is_project = True
        return new_writeable

    def __str__(self):
        full_path, _, _ = self._get_path()
        return full_path

    def _get_path(self):
        file_name_parts = [self._name[-1], DataSet.hash_metaarg(self._metaargs)]
        file_name_parts = [f for f in file_name_parts if f]
        filename = '.'.join(file_name_parts)
        if self._filesuffix:
            filename += "." + self._filesuffix
        datasetname = self._name[-1]
        project = '.'.join(self._name[:-1])
        full_path = os.path.join(self._prefix, os.path.join(project), filename)
        return full_path, datasetname, project

    def __fspath__(self):
        full_path, datasetname, project = self._get_path()
        cache.check_project_isnt_file(project)
        path_part = os.path.dirname(full_path)
        if not os.path.exists(path_part):
            os.makedirs(path_part)
        dataset = cache.get_or_create_dataset(
            datasetname,
            full_path,
            project,
            self._calling_filename,
            self._filesuffix,
            self._metaargs
        )
        cache.set_as_default(dataset)
        inputs._reset()
        return full_path

    def __repr__(self):
        """ TODO - put this only in the INPUT """
        full_path, datasetname, project = self._get_path()
        project_print = project + "." if project else ""
        header = "Project" if self._is_project else "Dataset" 
        return "{header}: {project}{dsn} local at {fp} {metaargs}".format(header=header, project=project_print, dsn=datasetname, fp=full_path, metaargs=self._metaargs)


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
