

default_branch = "master"


class _Settings(object):

    default_fileroot = "C:/tmp/play2/"
    default_metadata_fileroot =  default_fileroot + "_metadata/"

    local_datafile = 'C:/users/riguy/.datamaster/dbmaster.db'

    local_credentials_file = 'C:/users/riguy/.datamaster/token'

    remote_server = "http://127.0.0.1:8000/gettoken/"
    remote_server_sync_post = "http://127.0.0.1:8000/clientdataset/"

    active_branch = default_branch

    # path where settings were loaded from.
    _load_path = ""

    def save(self):
        """ Save from location that was used to load settings """
        print("TODO persist")

    @staticmethod
    def load(file_path):
        """ Load settings from a file and return _Settings object """ 
        if not file_path:
            print("TODO load settings")
            return _Settings()


settings = _Settings.load("")
