

class DataSetSerializer(object):

    def to_json_serializable(self, dataset):
        return {
            'metaargs_guid': dataset.metaargs_guid,
            'name': dataset.name,
            'project': dataset.project,
            'timepath': dataset.timepath,
            'last_modified_time': str(dataset.last_modified_time),
            'local_path': dataset.get_local_filename()
        }

    def from_dict(self, d):
        """ Rehydrates the DataSet, combining local knowledge with overrides from server """
        raise NotImplementedError()