import os
from .cache import cache
from .models import DatasetStates, DataSet
from .settings import default_fileroot


class ReadableFileName(os.PathLike):

    @staticmethod
    def _create_from_model(dataset):
        rfn = ReadableFileName(dataset.name, dataset.project)
        local_path = dataset.get_local_filename()
        if local_path:
            rfn._local_path = local_path
        rfn._set_doc(dataset)
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

    def _set_doc(self, dataset):
        metaargs = dataset.get_metaargs_str()
        if metaargs:
            self.__doc__ = metaargs
        else:
            self.__doc__ = "no metargs"

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("This is a readabile filename, used for inputs. You can't set new arguments for it!")

    def __repr__(self):
        if self._is_project:
            return "Project {project}".format(project=self._project)
        else:
            return "Dataset {project}.{name} at {path}".format(project=self._project, name=self._name, path=self._local_path)

    def __fspath__(self):
        # eventually this will need to ensure the file is local.
        return self._local_path # todo just look it up.


class DataMasterInput(object):
    """
    Provide paths for reading existing data.

    TODO:
        support a feature that wraps an existing data file. then it becomes a data file. Basically, delegate this to the output stuff.
    """

    def __init__(self):
        super(DataMasterInput, self).__init__()
        
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


