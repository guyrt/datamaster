from peewee import SqliteDatabase
import os
from .datamaster import DataMasterOutput
from .readablefile import inputs
from .settings import settings

import atexit

out = DataMasterOutput()

if not os.path.exists(settings.default_fileroot):
    os.makedirs(settings.default_fileroot)
