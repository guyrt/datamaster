from .filetools import make_paths
from .models import DataSet, DataSetFact, DataSetFactKeys


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
        source_file_contents = get_source_file(dataset)
        if source_file_contents:
            clientdataset_serialized.append({
                'key': DataSetFactKeys.CodeCopyContent, 
                'value': get_source_file(dataset)
            })

        return {
            'metaargs_guid': dataset.metaarg_guid,
            'name': dataset.name,
            'project': dataset.project,
            'timepath': dataset.timepath,
            'branch': dataset.branch.name,
            'local_machine_guid': dataset.guid,
            'latest_server_version': dataset.last_server_version,
            'facts': clientdataset_serialized
        }

    def from_dict(self, d):
        """ Rehydrates the DataSet, combining local knowledge with overrides from server """
        
        filesuffix = ''
        for key, value in d['facts'].items():
            pass

        # full_path, metadata_path, codecopy_path = make_paths(
        #     d['name'],
        #     d['project'],
        #     d['timepath'], , d['metaarg_guid'])

        dataset = DataSet.create(
            name=d['name'],
            project=d['project'],
            metaarg_guid=d['metaargs_guid'],
            timepath=d['timepath'],
            branch=d['branch'],
            last_server_version=d['latest_server_version'],
            local_machine_guid=d['local_machine_guid']
        )

        # todo - create state of remoteonly and use it.

        for key, value in d['facts'].items():
            if key == DataSetFactKeys.CodeCopyContent:
                pass
            else:
                DataSetFact.create(
                    dataset=dataset,
                    key=key,
                    value=value
                )

        return dataset


def get_source_file(dataset):
    file_name = dataset.get_fact(DataSetFactKeys.CodeCopyFilename)
    if not file_name:
        return None
    contents = open(file_name, 'r').read()
    return contents
