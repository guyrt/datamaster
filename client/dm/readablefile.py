import os
from .cache import cache, get_timepaths_for_dataset
from .models import DatasetStates, DataSet, ModelConstants
from .settings import default_fileroot


class ReadableProject(object):

    def __init__(self, project_name):
        self._project_name = project_name

    def __repr__(self):
        return "Project {project}".format(project=self._project_name)

    def _add_project(self, readable_project):
        setattr(self, readable_project._project_name, readable_project)

    def _add_file(self, readable_filename):
        setattr(self, readable_filename._name, readable_filename)


class ReadableFileName(os.PathLike):

    def __init__(self, dataset):
        self._prefix = default_fileroot
        self._local_path = ''
        self._metaargs = {}  # These can be used to version.

        self._set_info_from_model(dataset)

    def _set_info_from_model(self, dataset):
        self._dataset = dataset
        self._timepath = dataset.timepath
        self._name = dataset.name
        self._project = dataset.project
        
        local_path = dataset.get_local_filename()
        if local_path:
            # May be None if this is a remote file.
            self._local_path = local_path
    
    @property
    def __doc__(self):
        metaargs = self._dataset.get_metaargs_str()
        timestamp_info = get_timepaths_for_dataset(self._dataset)
        if 'allpaths' in timestamp_info:
            print(timestamp_info)
            timestamp_string = '\n'.join(['* ' + ts if ts == self._timepath else ts for ts in timestamp_info['allpaths']])
        else:
            timestamp_string = "{cnt} total values\nMin: {min_value}\nMax: {max_value}".format(**timestamp_string)
        if metaargs:
            return 'Timepaths:\n{1}\nMetaargs:\n{0}'.format(metaargs, timestamp_string)
        else:
            return "Timepaths:\n{0}".format(timestamp_string)

    @property
    def format(self):
        return self.metaargs.get(ModelConstants.FileFormat, '')

    @property
    def metaargs(self):
        return self._dataset.load_metaargs()

    def __call__(self, format=None, meta=None, timepath=''):
        timepath = timepath or self._timepath
        new_dataset = cache.get_dataset_by_args(self._dataset, format, meta, timepath)
        if not new_dataset:
            raise ValueError("No dataset found for arguments")
        if new_dataset.id == self._dataset.id:
            return self
        return ReadableFileName(new_dataset)

    def __repr__(self):
        return "Dataset {project}.{name} at {path} ".format(project=self._project, name=self._name, path=self._local_path)

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
        self._reset()

    def _reset(self):
        for dataset in cache.get_datasets(True):
            final_root = _create_project_tree(dataset, self)
            final_root._add_file(ReadableFileName(dataset))

    def _add_project(self, readable_project):
        setattr(self, readable_project._project_name, readable_project)

    def _add_file(self, readable_file):
        setattr(self, readable_file._name, readable_file)


def _create_project_tree(dataset : DataSet, root : DataMasterInput):
    if not dataset.project:
        return root
    project_parts = dataset.project.split('.')
    project_name = project_parts[0]
    if not hasattr(root, project_name):
        root._add_project(ReadableProject(project_name))
    current_root = getattr(root, project_name)
    for project_name in project_parts[1:]:
        if not hasattr(current_root, project_name):
            current_root._add_project(ReadableProject(project_name))
        current_root = getattr(current_root, project_name)
    return current_root


# Global variable that should be exported as the "inputs" entrypoint
inputs = DataMasterInput()
