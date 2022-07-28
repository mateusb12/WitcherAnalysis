from pathlib import Path

ref = Path(__file__).parent.parent


def get_data_path() -> Path:
    return Path(ref, 'data')


def get_webscrapping_path() -> Path:
    return Path(ref, 'webscrapping')


def get_driver_path() -> Path:
    return get_webscrapping_path() / 'geckodriver.exe'
