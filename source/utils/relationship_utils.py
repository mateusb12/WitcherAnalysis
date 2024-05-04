import numpy as np
import pandas as pd


def bidirectional_sort(input_dataframe: pd.DataFrame) -> pd.DataFrame:
    """ Sort cases where a→b and b→a"""
    sorted_table = np.sort(input_dataframe.values, axis=1)
    cols = input_dataframe.columns
    return pd.DataFrame(sorted_table, columns=cols)


def get_source_target_relationship_list(unique_list: list[str]) -> list:
    """Creates a list of tuples, where each tuple is a relationship between two characters
    Then returns a list of all the relationships, in the format {'source': source, 'target': target}"""
    if len(unique_list) <= 1:
        return []
    relationship_list = []
    for index, item in enumerate(unique_list):
        source = item
        target = unique_list[min(index + 1, len(unique_list) - 1)]
        if source != target:
            relationship_list.append({"source": source, "target": target})
    return relationship_list


def remove_string_duplicates(input_list: list[str]) -> list[str]:
    """Removes duplicates strings from a list of strings"""
    maximum_size = len(input_list) - 1
    unique_list = []
    for index, item in enumerate(input_list):
        current_item = item
        next_item = input_list[min(index + 1, maximum_size)]
        if current_item != next_item:
            unique_list.append(current_item)
    return unique_list
