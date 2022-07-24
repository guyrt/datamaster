import os
import shutil
import git

from .settings import settings


def make_folder(full_path):
    """Ensure that a folder exists for a given path"""
    path_part = os.path.dirname(full_path)
    
    if not os.path.exists(path_part):
        # ensure that the path exists.
        os.makedirs(path_part)
    

def make_paths(datasetname, project, timepath, filesuffix, hashed_metaargs):
    file_name_parts = datasetname

    if timepath:
        filename = os.path.join(file_name_parts, timepath, datasetname)
    else:
        filename = file_name_parts
    if filesuffix:
        filename += "." + filesuffix

    relative_path = os.path.join(settings.active_branch, os.path.join(project), hashed_metaargs, filename)
    full_path = os.path.join(settings.fileroot, relative_path)
    metadata_path = os.path.join(settings.metadata_fileroot, relative_path)

    full_path = os.path.normpath(full_path)
    metadata_path = os.path.normpath(metadata_path)
    make_folder(metadata_path)
    make_folder(full_path)
    return full_path, metadata_path


def copy_file(from_file, to_file):
    make_folder(to_file)
    shutil.copy2(from_file, to_file)


def get_clean_filename(iframe):
    """ Get a clean filename from the frame that called into DataMaster. """
    rawpath = iframe.f_code.co_filename
    if rawpath.startswith('<') and rawpath.endswith('>'):
        return settings.cmdline_filename
    full_path = os.path.abspath(rawpath)
    return full_path


def get_gitroot(full_path):
    """ Return the git root directory for a path if one exists. """
    try:
        git_repo = git.Repo(full_path, search_parent_directories=True)
    except git.NoSuchPathError:
        return {}
    git_root = git_repo.working_tree_dir
    current_commit = git_repo.head.commit
    #difs = git_repo.index.diff(None)
    # todo - compute diff for the calling file only.

    return {
        'git_root': git_root,
        'active_branch': git_repo.active_branch.name,
        'commit_hexsha': current_commit.hexsha,
        'commit_author': current_commit.author,
        'commit_authored_datetime': current_commit.authored_datetime
    }
