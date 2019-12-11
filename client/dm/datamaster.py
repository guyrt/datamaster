import git
import inspect
import os

from .cache import cache
from .filetools import make_folder
from .models import DatasetStates, DataSet
from .settings import settings
from .readablefile import inputs


class WriteableFileName(os.PathLike):
    """todo: class docstring"""

    def __init__(self, name, calling_filename):
        self._filesuffix = None
        self._metaargs = {}  # These can be used to version.
        self._is_project = False  # True iff this is not a file.
        self._timepath = None # Allows one to specify a path with timestamps.

        if type(name) == str:
            self._name = [name]
        else:
            self._name = name

        self._calling_filename = calling_filename

    def __call__(self, format=None, timepath=None, meta=None):
        if format:
            self._filesuffix = format
        if meta:
            self._metaargs = meta
        if timepath:
            if timepath[0] == '/':
                raise ValueError("Time paths cannot be absolute paths.")
            self._timepath = timepath
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
        full_path, _, _, _ = self._get_path()
        return full_path

    def _get_path(self):
        datasetname = self._name[-1]
        file_name_parts = datasetname

        if self._timepath:
            filename = os.path.join(file_name_parts, self._timepath, datasetname)
        else:
            filename = file_name_parts
        if self._filesuffix:
            filename += "." + self._filesuffix

        project = '.'.join(self._name[:-1])
        full_path = os.path.join(settings.default_fileroot, settings.active_branch, os.path.join(project), DataSet.hash_metaarg(self._metaargs), filename)
        metadata_path = os.path.join(settings.default_metadata_fileroot, settings.active_branch, os.path.join(project), DataSet.hash_metaarg(self._metaargs), filename)
        full_path = os.path.normpath(full_path)
        metadata_path = os.path.normpath(metadata_path)
        return full_path, metadata_path, datasetname, project

    def __fspath__(self):
        full_path, metadata_path, datasetname, project = self._get_path()
        cache.check_project_isnt_file(project)
        make_folder(full_path)

        dataset = cache.get_or_create_dataset(
            datasetname,
            full_path,
            metadata_path,
            project,
            self._calling_filename,
            self._timepath,
            self._filesuffix,
            self._metaargs
        )
        cache.set_as_default(dataset)
        inputs._reset()
        return full_path


class DataMasterOutput(object):
    """
    Provide paths for writing data.
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
