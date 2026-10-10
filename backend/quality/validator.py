from .models import QualityMeasurement, QualityRule, RuleType


def validate_measurement(
    measurement: QualityMeasurement,
    rule: QualityRule
) -> bool:

    if measurement.parameter != rule.parameter:
        raise ValueError(
            "Measurement and rule parameters do not match."
        )

    value = measurement.value

    if rule.rule_type in {
        RuleType.MAX,
        RuleType.MAX_STRICT,
        RuleType.MIN,
        RuleType.MIN_STRICT,
        RuleType.RANGE,
    }:
        if not isinstance(value, (int, float)):
            raise ValueError(
                "Numeric rules require a numeric measurement."
            )

    if rule.rule_type == RuleType.MAX:
        if rule.maximum is None:
            raise ValueError("MAX requires a maximum value.")
        return value <= rule.maximum

    if rule.rule_type == RuleType.MAX_STRICT:
        if rule.maximum is None:
            raise ValueError(
                "MAX_STRICT requires a maximum value."
            )
        return value < rule.maximum

    if rule.rule_type == RuleType.MIN:
        if rule.minimum is None:
            raise ValueError("MIN requires a minimum value.")
        return value >= rule.minimum

    if rule.rule_type == RuleType.MIN_STRICT:
        if rule.minimum is None:
            raise ValueError(
                "MIN_STRICT requires a minimum value."
            )
        return value > rule.minimum

    if rule.rule_type == RuleType.RANGE:
        if rule.minimum is None or rule.maximum is None:
            raise ValueError(
                "RANGE requires minimum and maximum values."
            )
        return rule.minimum <= value <= rule.maximum

    if rule.rule_type == RuleType.DESCRIPTIVE:
        if rule.expected is None:
            raise ValueError(
                "DESCRIPTIVE requires an expected value."
            )
        return (
            isinstance(value, str)
            and value.strip().casefold()
            == rule.expected.strip().casefold()
        )

    if rule.rule_type == RuleType.NIL:
        if isinstance(value, str):
            return value.strip().casefold() in {
                "nil",
                "none",
                "not detected",
            }

        if isinstance(value, (int, float)):
            return value == 0

        return False

    if rule.rule_type in {
        RuleType.AA,
        RuleType.NOT_APPLICABLE,
    }:
        raise NotImplementedError(
            f"{rule.rule_type.value} requires contextual "
            "interpretation and cannot be validated by a "
            "simple measurement comparison."
        )

    raise NotImplementedError(
        f"Rule type {rule.rule_type.value} is not supported."
    )