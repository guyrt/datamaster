import os
from typing import Any
import yaml

default_branch = "master"
default_authentication_path = '/gettoken/'
default_user_details_path = '/user/[UserSlug]'

user_root = os.path.expanduser("~")
user_path = os.path.join(user_root, '.datamaster/')
if not os.path.exists(user_path):
    os.mkdir(user_path)

dm_settings_filename = 'dmsettings.yaml'


class _RemotesCache(object):
    """ Handles tokens, provides lookup and save.
    
    Format:

    remotes:
        origin:
            user: <username>
            teams:
                <team slug>: 
                    urls:
                        sync: <>
                        ect: <>
            token: <token>
    """

    def __init__(self, local_credentials_file):
        self.local_credentials_file = local_credentials_file

    def retrieve_token(self, remote_name, username, team_slug):
        f = self.retrieve_remote(remote_name)
        try:
            return f['remotes'][remote_name][username][team_slug]
        except KeyError:
            print("No token found for {0} on team {1}. Did you login?".format(username, team_slug))

    def retrieve_remote(self, remote_name):
        f = self.get_file()
        try:
            return f['remotes'][remote_name]
        except KeyError:
            raise KeyError("No remote found for {0}".format(remote_name))

    def _get_empty_config(self):
        """ Set up default remote. The initial remote only has the gettoken, which lets one
        authenticate to retrieve the remainder of the urls.
        """

        return {
            'remotes': {
                'origin': create_remote('http://127.0.0.1:8000')
            }
        }

    def get_file(self):
        if os.path.exists(self.local_credentials_file):
            with open(self.local_credentials_file, 'r') as fh:
                f = yaml.full_load(fh)
                if not f:
                    return self._get_empty_config()
                if 'remotes' not in f:
                    raise ValueError("Corrupted remotes file {0}. You can remove it and reinitialize.".format(self.local_credentials_file))
                return f
        return self._get_empty_config()

    def save(self, contents):
        with open(self.local_credentials_file, 'w') as fh:
            yaml.dump(contents, fh)

    def update_remote(self, remote_name, username, team_info, token):
        f = self.get_file()
        if remote_name not in f['remotes']:
            raise ValueError("No remote {0}".format(remote_name))
        f['remotes'][remote_name]['username'] = username
        f['remotes'][remote_name]['token'] = token
        for team in team_info:
            team_slug = team['team_slug']
            if team_slug not in f['remotes'][remote_name]['teams']:
                f['remotes'][remote_name]['teams'][team_slug] = {'urls': dict()}
            f['remotes'][remote_name]['teams'][team_slug]['urls'].update(team['urls'])
        self.save(f)

    def add_remote(self, remote_name, remote_location, username, team_info, token):
        """Create a new remote and update with username and url info.

        The result of this operation should be that a remote is stored in
        the remotes file and is ready for authenticated use.
        """
        f = self.get_file()
        if remote_name in f['remotes']:
            raise ValueError("Cannot add remote {0}. It already exists. Try 'remote edit' to change it".format(remote_name))
        new_remote = create_remote(remote_location)
        new_remote['token'] = token
        new_remote['username'] = username
        for team in team_info:
            team_slug = team['team_slug']
            new_remote['teams'][team_slug] = {
                'urls': team['urls']
            }
        f['remotes'][remote_name] = new_remote
        self.save(f)


def create_remote(location):
    return {
        'location': location,
        'urls': {
            'remote_authentication': default_authentication_path,
            'remote_user_details': default_user_details_path
        },
        'teams': {}
    }


class _Settings(object):

    saveable_attributes = (
        'fileroot', 'metadata_fileroot', 'codecopy_fileroot',
        'local_database', 'active_remote', 'active_remote_team',
        'active_branch', 'active_remote_user'
    )

    fileroot = os.path.join(user_path, 'data')
    metadata_fileroot =  os.path.join(fileroot, '_metadata')
    codecopy_fileroot =  os.path.join(fileroot, '_codecopy')

    local_database = os.path.join(user_path, 'dbmaster.db')

    active_remote = 'origin'
    active_remote_team = 'datamastertest'
    active_branch = default_branch
    active_remote_user = 'guyrt'

    #
    # rarely updated by users
    # 

    # Used by the track cmd line option as the creating filename.
    cmdline_filename = "[cmdline]"

    # This should not be overridden and is not saved by default.
    # Credentials always flow from the user.
    local_credentials_file = os.path.join(user_path, 'remotes')

    def __init__(self, file_name=None) -> None:
        self._file_name = file_name
        self._loaded = False
        self._start_loading = False

    def __getattribute__(self, __name: str) -> Any:
        if __name.startswith('_'):
            return super(_Settings, self).__getattribute__(__name)
        if self._start_loading:
            return super(_Settings, self).__getattribute__(__name)
        if not self._loaded:
            self._load()
        return super(_Settings, self).__getattribute__(__name)
        
    def save_token(self, username, token_value, team_info):
        # todo - handle team_slugs.
        # if only 1, and global settings with none set, then set it to that one.
        # if >1 and global settings with none set, then ask.
        # if only 1 and local settings then override the one and warn user you did it.
        # if >1 and global settings then ask with option to keep current if it exists.
        token_handler = _RemotesCache(self.local_credentials_file)
        token_handler.update_remote(self.active_remote, username, team_info, token_value)

    def add_remote(self, remote_name, remote_host, username, team_info, token):
        token_handler = _RemotesCache(self.local_credentials_file)
        token_handler.add_remote(remote_name, remote_host, username, team_info, token)
        self.active_remote = remote_name
        self.save()

    def retrieve_token(self):
        """ Retrieve token based on active remote team and remote user """
        token_handler = _RemotesCache(self.local_credentials_file)
        return token_handler.retrieve_token(self.active_remote, self.active_remote_user, self.active_remote_team)

    def retrieve_remote(self):
        token_handler = _RemotesCache(self.local_credentials_file)
        return token_handler.retrieve_remote(self.active_remote)

    @staticmethod
    def lazy_load(file_name):
        """ Load settings from a file and return _Settings object """ 
        s = _Settings(file_name)
        return s

    def _load(self):
        if not self._file_name:
            return

        self._start_loading = True
        fh = open(self._file_name, 'r')
        raw_dict = yaml.full_load(fh)

        for k, v in raw_dict.items():
            if k == 'local_credentials_file':
                raise ValueError("Illegal to reset location of local_credentials_file")
            if not hasattr(self, k):
                raise ValueError("Unexpected key {0}".format(k))
            setattr(self, k, v)
        self._loaded = True
        self._start_loading = False

    def save(self):
        """ Save from location that was used to load settings """
        # todo - version these. don't destroy old settings (for debug)
        fh = open(get_metadata_in_root(), 'w')
        raw_dict = {k: getattr(self, k) for k in self.saveable_attributes}
        yaml.dump(raw_dict, fh)
        fh.close()


def get_metadata_in_root():
    cur_dir = os.path.abspath(os.path.curdir)
    previous_dir = ''
    while cur_dir != previous_dir:
        f = os.path.join(cur_dir, dm_settings_filename)
        if os.path.exists(f):
            return f
        previous_dir = cur_dir
        cur_dir = os.path.split(cur_dir)[0]
    settings_file = os.path.join(user_path, dm_settings_filename)
    return settings_file


def build_settings():
    settings_file = get_metadata_in_root()
    if not os.path.exists(settings_file):
        # No settings anywhere. Load from defaults.
        return _Settings()  
    return _Settings.lazy_load(settings_file)


# Todo - resolve file location from curdir. Start with current directory and work up the chain. if none then try user.
settings = build_settings()
