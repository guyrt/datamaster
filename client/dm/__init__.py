import os
from .datamaster import DataMasterOutput
from .writeablefile import DataMasterInput
from .settings import default_fileroot

import atexit

out = DataMasterOutput()
inputs = DataMasterInput()

if not os.path.exists(default_fileroot):
    os.makedirs(default_fileroot)
