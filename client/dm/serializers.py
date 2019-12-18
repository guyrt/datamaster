

class DataSetSerializer(object):

    def to_json_serializable(self, dataset):
        
        return {
            'metaargs_guid': dataset.metaarg_guid,
            'name': dataset.name,
            'project': dataset.project,
            'timepath': dataset.timepath,
            'branch': dataset.branch.name,
            'local_machine_guid': dataset.guid,
            'local_machine_time': str(dataset.last_modified_time),
            'local_path': dataset.get_local_filename(),
            'local_machine_name': dataset.get_local_machine_name()
        }

    def from_dict(self, d):
        """ Rehydrates the DataSet, combining local knowledge with overrides from server """
        raise NotImplementedError()