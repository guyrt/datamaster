import os

def make_folder(full_path):
    """Ensure that a folder exists for a given path"""
    path_part = os.path.dirname(full_path)
    
    if not os.path.exists(path_part):
        # ensure that the path exists.
        os.makedirs(path_part)
    