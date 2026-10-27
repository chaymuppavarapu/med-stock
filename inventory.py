from datetime import date, datetime, timedelta
from typing import Any

from medicine import next_id


WARNING_DAYS = 90


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("Dates must use YYYY-MM-DD format.") from error


def expiry_status(quantity: int, expiry_date: str, today: date | None = None) -> str:
    today = today or date.today()
    expiry = parse_date(expiry_date)
    if quantity == 0:
        return "OUT_OF_STOCK"
    if expiry < today:
        return "EXPIRED"
    if expiry <= today + timedelta(days=WARNING_DAYS):
        return "EXPIRING_SOON"
    return "IN_STOCK"


def make_batch(
    batches: list[dict[str, Any]],
    medicine_id: str,
    batch_number: str,
    received_date: str,
    expiry_date: str,
    quantity: int,
) -> dict[str, Any]:
    if not batch_number.strip():
        raise ValueError("Batch number is required.")
    if quantity <= 0:
        raise ValueError("Batch quantity must be greater than zero.")
    received = parse_date(received_date)
    expiry = parse_date(expiry_date)
    if expiry < received:
        raise ValueError("Expiry date cannot be before received date.")
    return {
        "id": next_id(batches, "BAT"),
        "medicine_id": medicine_id,
        "batch_number": batch_number.strip(),
        "received_date": received.isoformat(),
        "expiry_date": expiry.isoformat(),
        "quantity": quantity,
    }


def usable_stock(medicine_id: str, batches: list[dict[str, Any]], today: date | None = None) -> int:
    today = today or date.today()
    total = 0
    for batch in batches:
        if batch["medicine_id"] == medicine_id and parse_date(batch["expiry_date"]) >= today:
            total += max(0, batch["quantity"])
    return total


def change_stock(
    batches: list[dict[str, Any]],
    movements: list[dict[str, Any]],
    batch_id: str,
    movement_type: str,
    quantity: int,
    reason: str,
    today: date | None = None,
) -> dict[str, Any]:
    if quantity <= 0:
        raise ValueError("Movement quantity must be greater than zero.")
    if not reason.strip():
        raise ValueError("A reason is required.")
    batch = next((item for item in batches if item["id"] == batch_id), None)
    if batch is None:
        raise ValueError("Selected batch was not found.")

    status = expiry_status(batch["quantity"], batch["expiry_date"], today)
    if movement_type == "OUT":
        if status == "EXPIRED":
            raise ValueError("Stock-out is not allowed from an expired batch.")
        if quantity > batch["quantity"]:
            raise ValueError("Stock-out cannot be greater than available quantity.")
        batch["quantity"] -= quantity
    elif movement_type == "IN":
        batch["quantity"] += quantity
    else:
        raise ValueError("Movement type must be IN or OUT.")

    movement = {
        "id": next_id(movements, "MOV"),
        "batch_id": batch["id"],
        "medicine_id": batch["medicine_id"],
        "movement_type": movement_type,
        "quantity": quantity,
        "date_time": datetime.now().isoformat(timespec="seconds"),
        "reason": reason.strip(),
    }
    movements.append(movement)
    return movement

