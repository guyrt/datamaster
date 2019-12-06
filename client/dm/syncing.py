from .models import DataSetRemoteSync, DataSetRemoteSyncStates
from .serializers import DataSetSerializer




# This is the only remote we support right now. In future, consider storing more than one.
remotes = ['main']  

def create_stale_syncs(dataset):
    """ Creates stale syncs for all known remotes """
    for remote in remotes:
        DataSetRemoteSync.get_or_create(
            dataset=dataset,
            remote=remote,
            defaults={'sync_state': DataSetRemoteSyncStates.Stale}
        )


def sync():
    """
    Perform sync for every local, stale dataset.
    """
    need_sync = DataSetRemoteSync.select().where(DataSetRemoteSync.sync_state==DataSetRemoteSyncStates.Stale)
    for dataset_sync_state in need_sync:
        _push_dataset(dataset_sync_state.dataset)

def _push_dataset(dataset):
    """ Serialize a DataSet and push to server """
    import ipdb; ipdb.set_trace()
    serialized_dataset = DataSetSerializer(dataset)

    # add info about local machine
