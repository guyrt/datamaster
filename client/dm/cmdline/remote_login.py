from getpass import getpass
import requests

from ..settings import settings, default_authentication_path, default_user_details_path


def login(args):
    """Perform remote login based on user input args"""
    username, password = args.username, args.password
    if not args.password:
        password = getpass("Enter password: ")
    current_remote = settings.retrieve_remote()
    url = current_remote['location'] + current_remote['urls']['remote_authentication']

    token = login_with_password(url, username, password)
    if token:
        user_details = get_user_details(current_remote['location'], username, token, current_remote['urls']['remote_user_details'].replace('[UserSlug]', username))
        settings.save_token(username, token, user_details['membership_set'])
        print("success")


def login_with_password(url, username, password):
    try:
        results = requests.post(url, data={'username': username, 'password': password})
    except requests.ConnectionError:
        # TODO: log this!
        print("Endpoint {0} unavailable right now.".format(url))
        return None
    
    if results.status_code == 200:
        token = results.json()['token']
        return token
    elif results.status_code == 404:
        # TODO: log this!
        print("Endpoint {0} not found.".format(url))
    elif results.status_code == 400:
        errors = results.json()['non_field_errors']
        for e in errors:
            print(e)
    else:
        # TODO: log this!
        print("Unknown error.")
    return None


def get_user_details(current_remote_location, username, token, remote_user_details):
    """Retrieve details about user team memberships"""
    headers = {'Authorization': 'Token {0}'.format(token)}
    url = current_remote_location + remote_user_details
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    # TODO: log this
    raise ValueError("Error retrieving user details with new credentials")


def add_remote(args):
    """Add a new remote server using name and host"""
    host = args.host
    name = args.name
    username = args.username or input("Username for {0}: ".format(host))
    password = getpass("Enter password for {0}: ".format(host))
    # Attempt to authenticate
    url = host + default_authentication_path
    token = login_with_password(url, username, password)
    user_details_path = default_user_details_path.replace('[UserSlug]', username)
    user_details = get_user_details(host, username, token, user_details_path)
    settings.add_remote(name, host, username, user_details['membership_set'], token)
    print("Saved remote {1} as {0} and set to active. You should log in with 'sync'.".format(name, host))
