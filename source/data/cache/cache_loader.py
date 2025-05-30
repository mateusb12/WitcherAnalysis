from pathlib import Path

from path_reference.folder_reference import get_cache_path

NLP_CACHE_PATH = Path(get_cache_path(), "nlp_cache")
RELATIONSHIP_CACHE_PATH = Path(get_cache_path(), "relationship_cache")
ENTITY_CACHE_PATH = Path(get_cache_path(), "entity_cache")


def check_for_cache_file(path: Path, filename: str):
    path = Path(path, f"{filename}")
    return path.exists()


def existing_nlp_cache(filename: str) -> bool:
    return check_for_cache_file(NLP_CACHE_PATH, filename)


def existing_relationship_cache(filename: str) -> bool:
    return check_for_cache_file(RELATIONSHIP_CACHE_PATH, filename)


def existing_entity_cache(filename: str) -> bool:
    return check_for_cache_file(ENTITY_CACHE_PATH, filename)


def main():
    test = existing_nlp_cache("5 Baptism of Fire")
    print(test)


if __name__ == "__main__":
    main()
