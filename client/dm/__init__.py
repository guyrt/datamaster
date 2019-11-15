import os
from .datamaster import DataMasterOutput
from .readablefile import inputs
from .settings import default_fileroot

import atexit

out = DataMasterOutput()

if not os.path.exists(default_fileroot):
    os.makedirs(default_fileroot)
