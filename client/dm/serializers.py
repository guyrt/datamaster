from .models import DataSetFact


class DataSetFactSerializer(object):

    def to_json_serializable(self, datasetfact):
        return {
            'key': datasetfact.key,
            'value': datasetfact.value
        }


class DataSetSerializer(object):

    def to_json_serializable(self, dataset):
        
        clientdataset_facts = DataSetFact.select().where(DataSetFact.dataset==dataset)
        fact_serializer = DataSetFactSerializer()
        clientdataset_serialized = [fact_serializer.to_json_serializable(c) for c in clientdataset_facts]

        return {
            'metaargs_guid': dataset.metaarg_guid,
            'name': dataset.name,
            'project': dataset.project,
            'timepath': dataset.timepath,
            'branch': dataset.branch.name,
            'local_machine_guid': dataset.guid,
            'facts': clientdataset_serialized
        }

    def from_dict(self, d):
        """ Rehydrates the DataSet, combining local knowledge with overrides from server """
        raise NotImplementedError()