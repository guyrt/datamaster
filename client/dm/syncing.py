import requests

from .models import DataSetRemoteSync, DataSetRemoteSyncStates
from .serializers import DataSetSerializer
from .settings import settings
from .cmdline.remote_login import retrieve_token

# This is the only remote we support right now. In future, consider storing more than one.
remotes = ['main']  

def create_stale_syncs(dataset):
    """ Creates stale syncs for all known remotes """
    for remote in remotes:
        d, created = DataSetRemoteSync.get_or_create(
            dataset=dataset,
            remote=remote,
            defaults={'sync_state': DataSetRemoteSyncStates.Stale}
        )
        if not created:
            d.sync_state = DataSetRemoteSyncStates.Stale
            d.save()


def sync():
    """
    Perform sync for every local, stale dataset.
    """
    need_sync = DataSetRemoteSync.select().where(DataSetRemoteSync.sync_state==DataSetRemoteSyncStates.Stale)
    updates = 0
    for dataset_sync_state in need_sync:
        if not _push_dataset(dataset_sync_state.dataset):
            break
        else:
            q = DataSetRemoteSync.update({DataSetRemoteSync.sync_state: DataSetRemoteSyncStates.Synced}).where(DataSetRemoteSync.id==dataset_sync_state.id)
            q.execute()
            updates += 1
    print("Updated {0}".format(updates))


def _push_dataset(dataset):
    """ Serialize a DataSet and push to server """
    serialized_dataset = DataSetSerializer().to_json_serializable(dataset)

    serialized_dataset['team'] = 'datamastertest'
    serialized_dataset['user'] = 'guyrt'

    headers = {'Authorization': 'Token {0}'.format(retrieve_token())}
    
    response = requests.post(settings.remote_server_sync_post, data=serialized_dataset, headers=headers)
    if response.status_code < 200 or response.status_code >= 300:
        print(response.content)
        return False
    return True
