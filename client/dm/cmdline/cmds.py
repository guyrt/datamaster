""" Command line entrypoint """
import sys
import argparse

from .remote_login import login, add_remote
from ..syncing import push, pull
from .list_datasets import list_datasets
from .track import track_existing_path

dm_parser = argparse.ArgumentParser(description="Data Master!")

# Global args

_subparsers = dm_parser.add_subparsers(title="Subcommands", dest='action')
# Login
_login = _subparsers.add_parser("login", help="Get access credentials")
_login.set_defaults(func=login)
_login.add_argument("-u", "--username", dest="username", type=str, help='Remote username', required=True)
_login.add_argument("-p", "--password", dest="password", type=str, help='Leave blank to prompt for password', required=False)

# Remote
_remote = _subparsers.add_parser("remote", help="Manage remote server")
_remote_sub = _remote.add_subparsers(title="Remote subcommands", dest="remote_action")
_remote_add = _remote_sub.add_parser("add", help="Add a new remote server")
_remote_add.set_defaults(func=lambda x: add_remote(x))
_remote_add.add_argument('name')
_remote_add.add_argument('host', help="like https://www.datamaster.com")
_remote_add.add_argument("-u", "--username", dest="username", type=str, help='Remote username', required=False)

# Sync
_push = _subparsers.add_parser("push", help="Push locally created files to remote server")
_push.set_defaults(func=lambda x: push(x))
_push.add_argument("--force", dest='force_push', action='store_true')

_pull = _subparsers.add_parser("pull", help="Pull remote files from server")
_pull.set_defaults(func=lambda x: pull(x))

# List
_list = _subparsers.add_parser("list", help="List local datasets")
_list.set_defaults(func=lambda x: list_datasets())

# track
_track = _subparsers.add_parser("track", help="Track an existing dataset")
_track.set_defaults(func=lambda x: track_existing_path(x))
# TODO wait on syncing work _track.add_argument("--donotsync", dest='donotsync', action='store_true', help="Do not sync this file with the server. The existance of the file will sync, but the contents won't be available for other users.")
_track.add_argument("--keepext", dest='keepext', action='store_true', help="Keep the existing file extension.")
_track.add_argument("file")
_track.add_argument("name", help="Project and name of the dataset in project.subproject.datasetname format.")

def main():
    args = dm_parser.parse_args()

    if not vars(args) or not args.action:
        dm_parser.print_help()
        sys.exit(0)

    args.func(args)
