from peewee import SqliteDatabase
import os
from .datamaster import DataMasterOutput
from .readablefile import inputs
from .settings import settings

import atexit

out = DataMasterOutput()

if not os.path.exists(settings.fileroot):
    os.makedirs(settings.fileroot)
