import os
import shutil
from ..cache import cache
from ..datamaster import WriteableFileName
from ..settings import settings

def track_existing_path(args):
    filename = args.file
    filename = os.path.abspath(filename)
    full_name = args.name

    fname_parts = full_name.split('.')
    
    if not os.path.exists(filename):
        raise ValueError("Path {0} does not exist".format(filename))

    w = WriteableFileName(fname_parts, settings.cmdline_filename)

    if args.keepext:
        _, ext = os.path.splitext(filename)
        ext = ext[1:]
        w = w(format=ext)

    shutil.copy2(filename, w)
