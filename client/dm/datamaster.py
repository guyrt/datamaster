import getpass
import inspect
import json
import os
import socket
import sys
import logging
from dataclasses import dataclass

from .cache import cache
from .events import global_event_handler
from .filetools import get_clean_filename, get_gitroot, make_paths
from .models import DataSet
from .readablefile import inputs
from .settings import settings


@dataclass(frozen=True)
class OutputPath:
    full_path : str  # this is where data saves to - returned to user as a path.
    metadata_path : str  # this is where metadata is serialized to.
    dataset_name : str  # this is the part of full path that is same as file.
    project : str  # full project specifier - analogous to a path



class AuditKeys(object):
    """
    Todo - track all of these!
    """

    CallingFilename = 'calling_filename'
    CallingFilenameContentHash = 'calling_filename_content_hash'
    CodeCopyFilename = 'code_copy_filename'
    FileExtension = 'file_extension'
    LocalMachine = 'localmachine'
    LocalPath = 'localpath'
    LocalUsername = 'localusername'
    MetaArgFileName = 'metaargfilename'
    PreviousFileReads = 'previousfilereads'
    LoadedModules = 'loaded_modules'
    PythonVersion = 'python_version'
    State = 'state'

    # Git facts
    GitDetails = 'git'
    GitRoot = 'git_root'
    GitActiveBranch = 'git_active_branch'
    GitCommitHexSha = 'git_commit_hexsha'
    GitCommitAuthor = 'git_commit_author'
    GitCommitAuthoredDatetime = 'git_commit_authored_datetime'
    GitDiff = 'git_diff'
    GitUntracked = 'git_untracked'

    # Not stored in DB locally - used to send to server
    CodeCopyContent = 'code_copy_contents'
    
    
class MetadataWriter(object):

    def write_metadata(self, path : str, output_path_details : OutputPath, writeable_file : 'WriteableFileName'):
        """Write metadata to give path for a context. Take some care where you call this: (todo explain why)"""

        # make sure anything that goes in here is serialized or serializable.
        context = {
            AuditKeys.CallingFilename: writeable_file._calling_filename,
            AuditKeys.PreviousFileReads: self._serialize_filereads(global_event_handler.get_fileread()),
            AuditKeys.LocalMachine: socket.getfqdn(),
            AuditKeys.LocalUsername: getpass.getuser(),
            AuditKeys.LoadedModules: self._get_loaded_modules(),
            AuditKeys.PythonVersion: sys.version
        }
        if writeable_file._calling_filename:
            context[AuditKeys.GitRoot] = self._cache_git_info(writeable_file._calling_filename)

        data = {
            'dataset_name': output_path_details.dataset_name,
            'data_path': output_path_details.full_path,
            'project': output_path_details.project,
            'branch': settings.active_branch,
            'writeable_file_data': {
                'passed_metadata': writeable_file._metaargs,
                'file_suffix': writeable_file._file_suffix
            },
            'context': context
        }

        # todo - get metadata path and save.
        f = open(path, 'w')
        f.write(json.dumps(data, indent=2, sort_keys=True))
        f.close()

    def _serialize_filereads(self, datasets):
        if datasets is None:
            datasets = []
        return [d.guid for d in datasets]

    def _cache_git_info(self, creating_filename):
        """ Get information about git root, git commit/branch, and git diff. Set as facts """
        git_info = get_gitroot(creating_filename)
        if not git_info:
            return {}

        new_context = {
            AuditKeys.GitRoot: git_info['git_root'],
            AuditKeys.GitActiveBranch: git_info['active_branch'],
            AuditKeys.GitCommitHexSha: git_info['commit_hexsha'],
            AuditKeys.GitCommitAuthor: {
                'name': git_info['commit_author'].name,
                'email': git_info['commit_author'].email
            },
            AuditKeys.GitCommitAuthoredDatetime: str(git_info['commit_authored_datetime']),
            AuditKeys.GitDiff: git_info['diff'],
            AuditKeys.GitUntracked: git_info['untracked_files']
        }

        return new_context

    def _get_loaded_modules(self):
        import pkg_resources
        # list versions installed
        env = dict(tuple(str(ws).split()) for ws in pkg_resources.working_set)

        # list import modules
        module_keys = sys.modules.keys()

        loaded_package_versions = {}  # module => current version

        for module_key in sorted(module_keys):
            key_parts = module_key.split('.')
            for i in range(1, len(key_parts)):
                key = '.'.join(key_parts[:i])
                if key in loaded_package_versions:
                    break
                if key in env:
                    loaded_package_versions[key] = env[key]
                    break

        return loaded_package_versions


class WriteableFileName(os.PathLike):
    """Main entry point to get a writeable file."""

    def __init__(self, name, calling_filename):
        self._file_suffix = None
        self._metaargs = {}  # These can be used to version.
        self._is_project = False  # True iff this is not a file.
        self._timesuffix = None # Used to add text that isn't tracked as new entity

        if type(name) == str:
            self._name = [name]
        else:
            self._name = name

        self._calling_filename = calling_filename

    def __call__(self, extension=None, meta=None, timepath=None):
        if extension is not None:
            self._file_suffix = extension
        if meta is not None:
            self._metaargs = meta
        if timepath is not None:
            self._timesuffix = timepath

        if extension is not None and timepath is not None:
            raise ValueError("Unexpected inputs: extension and timepath can't be passed at same time.")

        return self

    def _set_internal_attributes(self, parent):
        self._file_suffix = parent._file_suffix
        self._metaargs = parent._metaargs

    def __getattribute__(self, name):
        """Name is playing the role of a new prefix, and this object has been converted to a 
        project or sub-project, not a specific folder."""
        if name.startswith("_"):
            return super(WriteableFileName, self).__getattribute__(name)
        new_writeable = WriteableFileName(self._name + [name], self._calling_filename)
        new_writeable._set_internal_attributes(self)
        self._is_project = True
        return new_writeable

    def __str__(self) -> str:
        """If something tries to make a string, treat it as a file."""
        return self.__fspath__()

    def _get_path(self) -> OutputPath:
        datasetname = self._name[-1]
        project = '.'.join(self._name[:-1])
        hashed_metaargs = DataSet.hash_metaarg(self._metaargs)
        full_path, metadata_path = make_paths(datasetname, project, self._file_suffix, hashed_metaargs, self._timesuffix)
        return OutputPath(full_path, metadata_path, datasetname, project)

    def __fspath__(self) -> str:
        """This is the point where we record the dataset as an object."""

        # Get the path where we will save data.
        path_data = self._get_path()
        cache.check_project_isnt_file(path_data.project)

        MetadataWriter().write_metadata(path_data.metadata_path, path_data, self)

        # make the tracking object
        dataset = cache.get_or_create_dataset(
            path_data.dataset_name,
            path_data.full_path,
            path_data.metadata_path,
            path_data.project,
            self._file_suffix,
            self._metaargs
        )

        # todo - make setting to do this.
        # Todo - set a latest.
        cache.set_as_default(dataset)

        # update inputs so this model appears.
        inputs._reset()
        return path_data.full_path

    def __add__(self, other: str) -> str:
        return os.path.join(str(self), other)


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
