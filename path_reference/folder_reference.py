from pathlib import Path

ref = Path(__file__).parent.parent


def get_data_path() -> Path:
    return Path(ref, 'data')
