import json
from pathlib import Path
from typing import Any


DATA_FOLDER = Path(__file__).parent / "data"


def load_records(file_name: str) -> list[dict[str, Any]]:
    """Load a list of records, using an empty list when the file is missing."""
    path = DATA_FOLDER / file_name
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(f"{path.name} contains invalid JSON.") from error

    if not isinstance(data, list):
        raise ValueError(f"{path.name} must contain a JSON list.")
    return data


def save_records(file_name: str, records: list[dict[str, Any]]) -> None:
    DATA_FOLDER.mkdir(exist_ok=True)
    path = DATA_FOLDER / file_name
    with path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)

