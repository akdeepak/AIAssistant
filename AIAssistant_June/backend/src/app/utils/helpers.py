import json
from typing import Any, Dict


def load_json(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r") as file:
        return json.load(file)


def save_json(data: Dict[str, Any], file_path: str) -> None:
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def flatten_dict(
    nested_dict: Dict[str, Any], parent_key: str = "", sep: str = "."
) -> Dict[str, Any]:
    items = {}
    for key, value in nested_dict.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.update(flatten_dict(value, new_key, sep=sep))
        else:
            items[new_key] = value
    return items


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict1.copy()
    merged.update(dict2)
    return merged


def get_nested_value(nested_dict: Dict[str, Any], keys: list) -> Any:
    for key in keys:
        nested_dict = nested_dict.get(key, {})
    return nested_dict
