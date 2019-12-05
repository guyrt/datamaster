from .models import DataSetRemoteSync, DataSetRemoteSyncStates

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
    
    need_sync = DataSetRemoteSync