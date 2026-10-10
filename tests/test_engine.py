import unittest

from backend.allocation.engine import (
    WaterDemand,
    allocate_water,
)

from backend.impact.calculator import calculate_impact


class TestWaterAllocation(unittest.TestCase):

    def setUp(self):
        """Create the demo facility's water demands."""
        self.demands = [
            WaterDemand(
                name="Toilet flushing",
                demand_litres=80_000,
                priority=3,
                compatible=True,
            ),
            WaterDemand(
                name="Landscaping",
                demand_litres=100_000,
                priority=2,
                compatible=True,
            ),
            WaterDemand(
                name="Vehicle washing",
                demand_litres=70_000,
                priority=1,
                compatible=True,
            ),
        ]

    def test_normal_supply(self):
        """Enough water should satisfy all three demo demands."""
        results = allocate_water(500_000, self.demands)

        allocated = {
            result.name: result.allocated_litres
            for result in results
        }

        self.assertEqual(allocated["Toilet flushing"], 80_000)
        self.assertEqual(allocated["Landscaping"], 100_000)
        self.assertEqual(allocated["Vehicle washing"], 70_000)

        total_allocated = sum(allocated.values())

        self.assertEqual(total_allocated, 250_000)
        self.assertEqual(500_000 - total_allocated, 250_000)

    def test_shortage_respects_priority(self):
        """Higher-priority uses should receive water first."""
        results = allocate_water(150_000, self.demands)

        allocated = {
            result.name: result.allocated_litres
            for result in results
        }

        self.assertEqual(allocated["Toilet flushing"], 80_000)
        self.assertEqual(allocated["Landscaping"], 70_000)
        self.assertEqual(allocated["Vehicle washing"], 0)

        self.assertEqual(
            sum(allocated.values()),
            150_000,
        )

    def test_incompatible_use_receives_no_water(self):
        """A use marked incompatible must not receive an allocation."""
        demands = [
            WaterDemand(
                name="Toilet flushing",
                demand_litres=80_000,
                priority=3,
                compatible=False,
            ),
            WaterDemand(
                name="Landscaping",
                demand_litres=100_000,
                priority=2,
                compatible=True,
            ),
        ]

        results = allocate_water(150_000, demands)

        allocated = {
            result.name: result.allocated_litres
            for result in results
        }

        self.assertEqual(allocated["Toilet flushing"], 0)
        self.assertEqual(allocated["Landscaping"], 100_000)

    def test_negative_supply_is_rejected(self):
        """Negative available water is invalid input."""
        with self.assertRaises(ValueError):
            allocate_water(-100, self.demands)

    def test_negative_demand_is_rejected(self):
        """Negative demand must not be accepted."""
        invalid_demands = [
            WaterDemand(
                name="Toilet flushing",
                demand_litres=-100,
                priority=3,
                compatible=True,
            )
        ]

        with self.assertRaises(ValueError):
            allocate_water(1_000, invalid_demands)


class TestWaterImpact(unittest.TestCase):

    def test_gross_savings_calculation(self):
        """250,000 litres at ₹50 per 1,000 litres."""
        result = calculate_impact(
            total_reused_litres=250_000,
            freshwater_cost_per_1000_litres=50,
        )

        self.assertEqual(
            result["estimated_freshwater_displaced_litres_per_day"],
            250_000,
        )

        self.assertEqual(
            result["estimated_gross_savings_per_day"],
            12_500,
        )

    def test_negative_water_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_impact(-100, 50)

    def test_negative_water_cost_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_impact(1_000, -50)


if __name__ == "__main__":
    unittest.main()