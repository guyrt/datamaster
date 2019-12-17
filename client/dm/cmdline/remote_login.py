from getpass import getpass
import requests

from ..settings import settings


def login(args):
    """Perform remote login based on user input args"""
    username, password = args.username, args.password
    if not args.password:
        password = getpass("Enter password: ")
    current_remote = settings.retrieve_remote()
    url = current_remote['location'] + current_remote['urls']['remote_authentication']

    try:
        results = requests.post(url, data={'username': username, 'password': password})
    except requests.ConnectionError:
        # TODO: log this!
        print("Endpoint {0} unavailable right now.".format(url))
        return
    
    if results.status_code == 200:
        token = results.json()['token']
        user_details = get_user_details(current_remote, username, token)
        settings.save_token(username, token, user_details['membership_set'])
        print("success")
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


def get_user_details(current_remote, username, token):
    """Retrieve details about user team memberships"""
    headers = {'Authorization': 'Token {0}'.format(token)}
    url = current_remote['location'] + current_remote['urls']['remote_user_details'].replace('[UserSlug]', username)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()

    # TODO: log this
    raise ValueError("Error retrieving user details with new credentials")
