import unittest

from backend.planner import (
    assess_use,
    create_allocation_plan,
)

from backend.quality.models import (
    QualityMeasurement,
    QualityRule,
    RuleType,
)

from backend.allocation.engine import WaterDemand


class TestWaterPlanner(unittest.TestCase):

    def setUp(self):
        self.toilet_rules = [
            QualityRule(
                parameter="turbidity",
                rule_type=RuleType.MAX_STRICT,
                unit="NTU",
                maximum=2,
            )
        ]

        self.measurements = [
            QualityMeasurement(
                parameter="turbidity",
                value=1.4,
                unit="NTU",
            )
        ]

    def test_passing_configured_rule(self):
        result = assess_use(
            self.measurements,
            self.toilet_rules,
        )

        self.assertTrue(result["eligible"])
        self.assertEqual(result["status"], "RULES_PASSED")

    def test_failed_quality_rule(self):
        failed_measurements = [
            QualityMeasurement(
                parameter="turbidity",
                value=2.0,
                unit="NTU",
            )
        ]

        result = assess_use(
            failed_measurements,
            self.toilet_rules,
        )

        self.assertFalse(result["eligible"])
        self.assertEqual(result["status"], "NOT_ELIGIBLE")

    def test_missing_measurement(self):
        result = assess_use(
            [],
            self.toilet_rules,
        )

        self.assertFalse(result["eligible"])
        self.assertTrue(result["reasons"])

    def test_missing_rule_configuration(self):
        result = assess_use(
            self.measurements,
            [],
        )

        self.assertFalse(result["eligible"])
        self.assertEqual(
            result["status"],
            "INSUFFICIENT_DATA",
        )

    def test_ineligible_use_receives_no_water(self):
        demands = [
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
        ]

        plan = create_allocation_plan(
            available_litres=150_000,
            demands=demands,
            measurements=[
                QualityMeasurement(
                    parameter="turbidity",
                    value=2.0,
                    unit="NTU",
                )
            ],
            rules_by_use={
                "Toilet flushing": self.toilet_rules,
                # No verified rules configured for landscaping.
            },
            freshwater_cost_per_1000_litres=50,
        )

        allocations = {
            item["name"]: item["allocated_litres"]
            for item in plan["allocations"]
        }

        self.assertEqual(
            allocations["Toilet flushing"],
            0,
        )

        self.assertEqual(
            allocations["Landscaping"],
            0,
        )

        self.assertEqual(
            plan["total_allocated_litres"],
            0,
        )


if __name__ == "__main__":
    unittest.main()