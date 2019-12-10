""" Command line entrypoint """
import sys
import argparse

from .remote_login import login
from ..syncing import sync
from .list_datasets import list_datasets

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

# Sync
_sync = _subparsers.add_parser("sync", help="Sync to remote server")
_sync.set_defaults(func=lambda x: sync())
# Todo - likely want to sync to a specific remote.

# List
_list = _subparsers.add_parser("list", help="List local datasets")
_list.set_defaults(func=lambda x: list_datasets())

args = dm_parser.parse_args()

if not vars(args) or not args.action:
    dm_parser.print_help()
    sys.exit(0)

args.func(args)
