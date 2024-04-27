from pathlib import Path


def handle_new_folder(output_location):
    """ Create a new output folder if it doesn't already exist, with an __init__.py` file inside. """
    output_folder = output_location.parent
    if not output_folder.exists():
        output_folder.mkdir(parents=True)
        Path(output_folder, "__init__.py").touch()
