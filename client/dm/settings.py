import os
import yaml

default_branch = "master"

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
            print("No remote found for {0}".format(remote_name))

    def _get_empty_config(self):
        """ Set up default remote. The initial remote only has the gettoken, which lets one
        authenticate to retrieve the remainder of the urls.
        """

        return {
            'remotes': {
                'origin': {
                    'location': 'http://127.0.0.1:8000',
                    'urls': {
                        'remote_authentication': '/gettoken/',
                        'remote_user_details': '/user/[UserSlug]'
                    },
                    'teams': {}
                }
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


class _Settings(object):

    fileroot = os.path.join(user_path, 'data')
    metadata_fileroot =  os.path.join(fileroot, '_metadata')

    local_database = os.path.join(user_path, 'dbmaster.db')

    # This should not be overridden and is not saved by default.
    # Credentials always flow from the user.
    local_credentials_file = os.path.join(user_path, 'remotes')

    active_remote = 'origin'
    active_remote_team = 'datamastertest'
    active_branch = default_branch
    active_remote_user = 'guyrt'

    def save(self):
        """ Save from location that was used to load settings """
        print("TODO persist")

    def save_token(self, username, token_value, team_info):
        # todo - handle team_slugs.
        # if only 1, and global settings with none set, then set it to that one.
        # if >1 and global settings with none set, then ask.
        # if only 1 and local settings then override the one and warn user you did it.
        # if >1 and global settings then ask with option to keep current if it exists.
        token_handler = _RemotesCache(self.local_credentials_file)
        token_handler.update_remote(self.active_remote, username, team_info, token_value)

    def retrieve_token(self):
        """ Retrieve token based on active remote team and remote user """
        token_handler = _RemotesCache(self.local_credentials_file)
        return token_handler.retrieve_token(self.active_remote, self.active_remote_user, self.active_remote_team)

    def retrieve_remote(self):
        token_handler = _RemotesCache(self.local_credentials_file)
        return token_handler.retrieve_remote(self.active_remote)

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
