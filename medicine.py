from datetime import date
from typing import Any


def next_id(records: list[dict[str, Any]], prefix: str) -> str:
    numbers = [
        int(record["id"][len(prefix):])
        for record in records
        if record.get("id", "").startswith(prefix)
        and record["id"][len(prefix):].isdigit()
    ]
    return f"{prefix}{max(numbers, default=0) + 1:03d}"


def validate_medicine(name: str, reorder_level: int) -> str | None:
    if not name.strip():
        return "Medicine name is required."
    if reorder_level < 0:
        return "Reorder level cannot be negative."
    return None


def make_medicine(
    medicines: list[dict[str, Any]],
    name: str,
    category: str,
    unit: str,
    reorder_level: int,
) -> dict[str, Any]:
    error = validate_medicine(name, reorder_level)
    if error:
        raise ValueError(error)
    return {
        "id": next_id(medicines, "MED"),
        "name": name.strip(),
        "category": category.strip(),
        "unit": unit.strip() or "unit",
        "reorder_level": reorder_level,
        "is_active": True,
    }


def find_medicine(medicines: list[dict[str, Any]], medicine_id: str) -> dict[str, Any] | None:
    return next((medicine for medicine in medicines if medicine["id"] == medicine_id), None)

