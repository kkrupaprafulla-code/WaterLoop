import unittest

from backend.quality.models import (
    QualityMeasurement,
    QualityRule,
    RuleType,
)
from backend.quality.validator import validate_measurement


class TestQualityValidator(unittest.TestCase):

    def test_strict_maximum(self):
        rule = QualityRule(
            parameter="turbidity",
            rule_type=RuleType.MAX_STRICT,
            maximum=2,
        )

        self.assertTrue(
            validate_measurement(
                QualityMeasurement("turbidity", 1.4),
                rule,
            )
        )

        self.assertFalse(
            validate_measurement(
                QualityMeasurement("turbidity", 2.0),
                rule,
            )
        )

    def test_inclusive_maximum(self):
        rule = QualityRule(
            parameter="bod",
            rule_type=RuleType.MAX,
            maximum=6,
        )

        self.assertTrue(
            validate_measurement(
                QualityMeasurement("bod", 6),
                rule,
            )
        )

        self.assertFalse(
            validate_measurement(
                QualityMeasurement("bod", 6.1),
                rule,
            )
        )

    def test_inclusive_minimum(self):
        rule = QualityRule(
            parameter="chlorine",
            rule_type=RuleType.MIN,
            minimum=1,
        )

        self.assertTrue(
            validate_measurement(
                QualityMeasurement("chlorine", 1),
                rule,
            )
        )

        self.assertFalse(
            validate_measurement(
                QualityMeasurement("chlorine", 0.9),
                rule,
            )
        )

    def test_strict_minimum(self):
        rule = QualityRule(
            parameter="example",
            rule_type=RuleType.MIN_STRICT,
            minimum=5,
        )

        self.assertFalse(
            validate_measurement(
                QualityMeasurement("example", 5),
                rule,
            )
        )

        self.assertTrue(
            validate_measurement(
                QualityMeasurement("example", 5.1),
                rule,
            )
        )

    def test_range_including_boundaries(self):
        rule = QualityRule(
            parameter="ph",
            rule_type=RuleType.RANGE,
            minimum=6.5,
            maximum=8.5,
        )

        for value in (6.5, 7.2, 8.5):
            with self.subTest(value=value):
                self.assertTrue(
                    validate_measurement(
                        QualityMeasurement("ph", value),
                        rule,
                    )
                )

        self.assertFalse(
            validate_measurement(
                QualityMeasurement("ph", 8.6),
                rule,
            )
        )

    def test_descriptive_value(self):
        rule = QualityRule(
            parameter="colour",
            rule_type=RuleType.DESCRIPTIVE,
            expected="colourless",
        )

        self.assertTrue(
            validate_measurement(
                QualityMeasurement("colour", "Colourless"),
                rule,
            )
        )

        self.assertFalse(
            validate_measurement(
                QualityMeasurement("colour", "brown"),
                rule,
            )
        )

    def test_nil_numeric_value(self):
        rule = QualityRule(
            parameter="oil_grease",
            rule_type=RuleType.NIL,
        )

        self.assertTrue(
            validate_measurement(
                QualityMeasurement("oil_grease", 0),
                rule,
            )
        )

        self.assertFalse(
            validate_measurement(
                QualityMeasurement("oil_grease", 0.1),
                rule,
            )
        )

    def test_parameter_mismatch_is_rejected(self):
        rule = QualityRule(
            parameter="turbidity",
            rule_type=RuleType.MAX_STRICT,
            maximum=2,
        )

        with self.assertRaises(ValueError):
            validate_measurement(
                QualityMeasurement("ph", 7.2),
                rule,
            )

    def test_numeric_rule_rejects_text(self):
        rule = QualityRule(
            parameter="turbidity",
            rule_type=RuleType.MAX_STRICT,
            maximum=2,
        )

        with self.assertRaises(ValueError):
            validate_measurement(
                QualityMeasurement("turbidity", "unknown"),
                rule,
            )


if __name__ == "__main__":
    unittest.main()