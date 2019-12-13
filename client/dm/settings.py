import os
import yaml

default_branch = "master"

user_root = os.path.expanduser("~")
user_path = os.path.join(user_root, '.datamaster/')
if not os.path.exists(user_path):
    os.mkdir(user_path)


dm_settings_filename = 'dmsettings.yaml'


class _Settings(object):

    fileroot = os.path.join(user_path, 'data')
    metadata_fileroot =  os.path.join(fileroot, '_metadata')

    local_database = os.path.join(user_path, 'dbmaster.db')

    # This should not be overridden and is not saved by default.
    #  Credentials always flow from the user.
    local_credentials_file = os.path.join(user_path, 'token')

    # TODO - set these URLs by querying the remote for its URLs.
    remote_server = "http://127.0.0.1:8000/gettoken/"
    remote_server_sync_post = "http://127.0.0.1:8000/clientdataset/"

    active_branch = default_branch

    def save(self):
        """ Save from location that was used to load settings """
        print("TODO persist")

    @staticmethod
    def load(file_handle):
        """ Load settings from a file and return _Settings object """ 
        raw_dict = yaml.full_load(file_handle)
        s = _Settings()
        for k, v in raw_dict.items():
            if k == 'local_credentials_file':
                raise ValueError("Illegal to reset location of local_credentials_file")
            if not hasattr(s, k):
                raise ValueError("Unexpected key {0}".format(k))
            setattr(s, k, v)
        return s


def get_metadata_in_root():
    cur_dir = os.path.abspath(os.path.curdir)
    previous_dir = ''
    while cur_dir != previous_dir:
        f = os.path.join(cur_dir, dm_settings_filename)
        if os.path.exists(f):
            return f
        previous_dir = cur_dir
        cur_dir = os.path.split(cur_dir)[0]
    return None


def build_settings():
    settings_file = get_metadata_in_root()
    if not settings_file:
        # Didn't exist - use user folder
        settings_file = os.path.join(user_path, dm_settings_filename)
        if not os.path.exists(settings_file):
            # No settings anywhere. Load from defaults.
            return _Settings()  
    return _Settings.load(open(settings_file, 'r'))

# Todo - resolve file location from curdir. Start with current directory and work up the chain. if none then try user.
settings = build_settings()
