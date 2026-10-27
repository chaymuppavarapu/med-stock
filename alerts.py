from datetime import date
from typing import Any

from inventory import expiry_status, usable_stock


def expired_batches(batches: list[dict[str, Any]], today: date | None = None) -> list[dict[str, Any]]:
    return [batch for batch in batches if expiry_status(batch["quantity"], batch["expiry_date"], today) == "EXPIRED"]


def near_expiry_batches(batches: list[dict[str, Any]], today: date | None = None) -> list[dict[str, Any]]:
    return [
        batch
        for batch in batches
        if expiry_status(batch["quantity"], batch["expiry_date"], today) == "EXPIRING_SOON"
    ]


def low_stock_medicines(
    medicines: list[dict[str, Any]],
    batches: list[dict[str, Any]],
    today: date | None = None,
) -> list[dict[str, Any]]:
    return [
        medicine
        for medicine in medicines
        if medicine["is_active"]
        and usable_stock(medicine["id"], batches, today) <= medicine["reorder_level"]
    ]

