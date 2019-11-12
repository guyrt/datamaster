import os
import inspect
import git
from .cache import DataMasterCache
from .models import DatasetStates, DataSet
from .setting import default_fileroot


if not os.path.exists(default_fileroot):
    os.makedirs(default_fileroot)


cache = DataMasterCache()


class ReadableFileName(os.PathLike):
    
    @staticmethod
    def _create_from_model(dataset):
        rfn = ReadableFileName(dataset.name, dataset.project)
        local_path = dataset.get_local_filename()
        if local_path:
            rfn._local_path = local_path
        return rfn

    @staticmethod
    def _create_project(project_name):
        rfn = ReadableFileName(project_name, None)  # todo handle nested projects
        rfn._is_project = True
        return rfn

    def __init__(self, name, project):
        self._prefix = default_fileroot
        self._metaargs = {}  # These can be used to version.
        self._is_project = False  # True iff this is not a file.

        self._name = name
        self._project = project
        self._local_path = None

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("This is a readabile filename, used for inputs. You can't set new arguments for it!")

    def __repr__(self):
        if self._is_project:
            return "Project"
        else:
            return "Dataset {project}.{name} at {path}".format(project=self._project, name=self._name, path=self._local_path)

    def __fspath__(self):
        # eventually this will need to ensure the file is local.
        return self._local_path # todo just look it up.


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

    def __call__(self, **kwargs):
        if 'format' in kwargs:
            self._filesuffix = kwargs['format']
        if 'meta' in kwargs:
            self._metaargs = kwargs['meta']
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
        path_part = os.path.dirname(full_path)
        if not os.path.exists(path_part):
            os.makedirs(path_part)
        dataset = cache.get_or_create_dataset(datasetname, full_path, project, DatasetStates.LocalDeclared, self._calling_filename, self._metaargs)
        cache.set_as_default(dataset)
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


class DataMasterInput(object):
    """
    Provide paths for reading existing data.

    TODO:
        support a feature that wraps an existing data file. then it becomes a data file. Basically, delegate this to the output stuff.
    """

    def __init__(self):
        super(DataMasterInput, self).__init__()
        
        cache = DataMasterCache()
        for dataset in cache.get_datasets(True):
            final_root = _create_project_tree(dataset, self)
            setattr(final_root, dataset.name, ReadableFileName._create_from_model(dataset))


def _create_project_tree(dataset : DataSet, root : DataMasterInput):
    if not dataset.project:
        return root
    project_parts = dataset.project.split('.')
    project_name = project_parts[0]
    if not hasattr(root, project_name):
        setattr(root, project_name, ReadableFileName._create_project(project_name))
    current_root = getattr(root, project_name)
    for project_name in project_parts[1:]:
        # update - need to make ReadableFileNames if they don't have them.
        current_root = getattr(current_root, project_name)
    return current_root


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
