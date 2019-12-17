from getpass import getpass
import requests

from ..settings import settings


def login(args):
    """Perform remote login based on user input args"""
    username, password = args.username, args.password
    if not args.password:
        password = getpass("Enter password: ")
    url = settings.retrieve_remote()['remote_authentication_url']

    try:
        results = requests.post(url, data={'username': username, 'password': password})
    except requests.ConnectionError:
        # TODO: log this!
        print("Endpoint {0} unavailable right now.".format(url))
        return
    
    if results.status_code == 200:
        # TODO - get urls and get the possible teams.
        settings.save_token(username, results.json()['token'], {})
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


def get_user_details(username):
    