import unittest
from datetime import date, timedelta

from alerts import low_stock_medicines
from inventory import change_stock, expiry_status, make_batch, usable_stock
from medicine import make_medicine


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.medicines = []
        self.batches = []
        self.movements = []
        self.medicine = make_medicine(self.medicines, "Paracetamol", "Pain relief", "tablets", 10)
        self.medicines.append(self.medicine)

    def test_expiry_statuses(self):
        today = date(2026, 10, 27)
        self.assertEqual(expiry_status(0, "2026-10-27", today), "OUT_OF_STOCK")
        self.assertEqual(expiry_status(5, "2026-10-26", today), "EXPIRED")
        self.assertEqual(expiry_status(5, "2026-10-27", today), "EXPIRING_SOON")
        self.assertEqual(expiry_status(5, "2027-02-01", today), "IN_STOCK")

    def test_stock_out_failure_does_not_change_data(self):
        batch = make_batch(self.batches, self.medicine["id"], "B1", "2026-01-01", "2027-01-01", 5)
        self.batches.append(batch)
        with self.assertRaises(ValueError):
            change_stock(self.batches, self.movements, batch["id"], "OUT", 6, "Sale")
        self.assertEqual(batch["quantity"], 5)
        self.assertEqual(self.movements, [])

    def test_stock_and_low_stock(self):
        batch = make_batch(self.batches, self.medicine["id"], "B1", "2026-01-01", "2027-01-01", 5)
        self.batches.append(batch)
        change_stock(self.batches, self.movements, batch["id"], "IN", 10, "New delivery")
        self.assertEqual(usable_stock(self.medicine["id"], self.batches), 15)
        self.assertEqual(len(low_stock_medicines(self.medicines, self.batches)), 0)


if __name__ == "__main__":
    unittest.main()
