from peewee import SqliteDatabase
import os
from .datamaster import DataMasterOutput
from .readablefile import inputs  # keep this
from .settings import settings

outputs = DataMasterOutput()

if not os.path.exists(settings.fileroot):
    os.makedirs(settings.fileroot)


try:
    from py4j.protocol import register_input_converter
    from .converters import WriteableFileNameConverter
    
    register_input_converter(WriteableFileNameConverter())
except ModuleNotFoundError:
    pass  # if no py4j then don't run converters
