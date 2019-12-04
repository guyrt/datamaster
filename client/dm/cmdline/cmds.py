""" Command line entrypoint """
import sys
import argparse

import remote_login


dm_parser = argparse.ArgumentParser(description="Data Master!")

# Global args

_subparsers = dm_parser.add_subparsers(title="Subcommands", dest='action')
# Login
_login = _subparsers.add_parser("login", help="Get access credentials")
_login.set_defaults(func=remote_login.login)
_login.add_argument("-u", "--username", dest="username", type=str, help='Remote username', required=True)
_login.add_argument("-p", "--password", dest="password", type=str, help='Leave blank to prompt for password', required=False)

# Remote
_remote = _subparsers.add_parser("remote", help="Manage remote server")


args = dm_parser.parse_args()
if not vars(args):
    dm_parser.print_help()
    sys.exit(0)

args.func(args)