from getpass import getpass
import requests

from ..settings import settings

def get_server():
    # todo load from settings
    return settings.remote_server


def save_token(token_value):
    f = open(settings.local_credentials_file, 'w')
    f.write(token_value)
    f.close()

def retrieve_token():
    f = open(settings.local_credentials_file, 'r')
    return f.read()

def login(args):
    """Perform remote login based on user input args"""
    username, password = args.username, args.password
    if not args.password:
        password = getpass("Enter password: ")
    url = get_server()

    try:
        results = requests.post(url, data={'username': username, 'password': password})
    except requests.ConnectionError:
        # TODO: log this!
        print("Endpoint {0} unavailable right now.".format(url))
        return
    
    if results.status_code == 200:
        save_token(results.json()['token'])
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
