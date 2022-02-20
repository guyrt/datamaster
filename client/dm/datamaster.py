import inspect
import os

from .cache import cache
from .events import global_event_handler
from .filetools import make_folder, make_paths, get_clean_filename
from .models import DataSet
from .settings import settings
from .readablefile import inputs


class WriteableFileName(os.PathLike):
    """Main entry point to get a writeable file."""

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

    def __call__(self, extension=None, timepath=None, meta=None):
        if extension:
            self._filesuffix = extension
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

    def __str__(self) -> str:
        """If something tries to make a string, treat it as a file."""
        return self.__fspath__()

    def _get_path(self):
        datasetname = self._name[-1]
        project = '.'.join(self._name[:-1])
        hashed_metaargs = DataSet.hash_metaarg(self._metaargs)
        full_path, metadata_path, _ = make_paths(datasetname, project, self._timepath, self._filesuffix, hashed_metaargs)
        return full_path, metadata_path, datasetname, project

    def __fspath__(self) -> str:
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
            self._metaargs,
            global_event_handler.get_fileread()
        )
        cache.set_as_default(dataset)
        inputs._reset()
        return full_path


class DataMasterOutput(object):
    """
    Provide paths for writing data.
    """

    def __getattribute__(self, name):
        if name.startswith("_"):
            return super(DataMasterOutput, self).__getattribute__(name)
        iframe = inspect.currentframe().f_back
        calling_filename = get_clean_filename(iframe)
        return WriteableFileName(name, calling_filename)

