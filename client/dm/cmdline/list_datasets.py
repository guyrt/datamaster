# Inspection utilities for local use.

from dm.models import DataSet


def list_datasets():
    """ List datasets that exist locally """
    datasets = DataSet.select().order_by(DataSet.is_default.desc())
    dataset_grouping = {}
    for dataset in datasets:
        ds_key = dataset.full_name
        project = dataset.project
        if project not in dataset_grouping:
            dataset_grouping[project] = {}
        if ds_key not in dataset_grouping[project]:
            dataset_grouping[project][ds_key] = []
        dataset_grouping[project][ds_key].append(dataset)
    print(_datasets_to_string(dataset_grouping))
    
def _datasets_to_string(dataset_grouping):
    s = ''
    for project, datasets in dataset_grouping.items():
        s += "Project: {0}\n".format(project)
        for dataset_name, dataset_objs in datasets.items():
            s += "\t{0}\n".format(dataset_name)
            for dataset_obj in dataset_objs:
                s += "\t\t{0}\n".format(_single_dataset_to_string(dataset_obj))
        s += "\n"
    return s

def _single_dataset_to_string(dataset):
    s = "*** " if dataset.is_default else "    "
    s += dataset.get_local_filename()
    return s


if __name__ == "__main__":
    list_datasets()