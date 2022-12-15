import sys
from pathlib import Path


def is_path_reference_folder_reachable():
    core_folder = Path(__file__).parent.parent
    ref = str(Path(core_folder, "path_reference"))
    path = sys.path
    return ref in path


def fix_non_reachable_path():
    core_folder = Path(__file__).parent.parent
    ref = str(Path(core_folder, "path_reference"))
    sys.path.append(ref)
    sys.path.append(str(core_folder))


fix_non_reachable_path()
