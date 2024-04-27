import sys
from pathlib import Path


def is_path_reference_folder_reachable():
    """This function is used to check if the path_reference folder is reachable from the current file."""
    core_folder = Path(__file__).parent.parent
    ref = str(Path(core_folder, "path_reference"))
    path = sys.path
    return ref in path


def fix_non_reachable_path():
    """This function is used to fix the path_reference folder not being reachable from the current file.
    Its main purpose is to fix NoModuleFoundError when running the code from jupyter notebooks"""
    core_folder = Path(__file__).parent.parent
    ref = str(Path(core_folder, "path_reference"))
    sys.path.append(ref)
    sys.path.append(str(core_folder))


fix_non_reachable_path()
