from backend.quality.models import (
    QualityMeasurement,
    QualityRule,
)
from backend.quality.validator import validate_measurement
from backend.allocation.engine import (
    WaterDemand,
    allocate_water,
)
from backend.impact.calculator import calculate_impact


def assess_use(
    measurements: list[QualityMeasurement],
    required_rules: list[QualityRule],
) -> dict:
    """
    Assess one intended use against its configured quality rules.

    Missing measurements or rules that require contextual
    interpretation prevent the use from being approved.
    """

    if not required_rules:
        return {
            "eligible": False,
            "status": "INSUFFICIENT_DATA",
            "reasons": ["No quality rules are configured."],
        }

    measurement_map = {
        measurement.parameter: measurement
        for measurement in measurements
    }

    reasons = []

    for rule in required_rules:
        measurement = measurement_map.get(rule.parameter)

        if measurement is None:
            reasons.append(
                f"Missing measurement: {rule.parameter}"
            )
            continue

        try:
            passed = validate_measurement(measurement, rule)
        except (ValueError, NotImplementedError) as error:
            reasons.append(
                f"{rule.parameter}: {error}"
            )
            continue

        if not passed:
            reasons.append(
                f"{rule.parameter} failed its configured rule."
            )

    if reasons:
        return {
            "eligible": False,
            "status": "NOT_ELIGIBLE",
            "reasons": reasons,
        }

    return {
        "eligible": True,
        "status": "RULES_PASSED",
        "reasons": [
            "Configured checks passed; this is not regulatory "
            "certification or proof of overall suitability."
        ],
    }


def create_allocation_plan(
    available_litres: float,
    demands: list[WaterDemand],
    measurements: list[QualityMeasurement],
    rules_by_use: dict[str, list[QualityRule]],
    freshwater_cost_per_1000_litres: float,
) -> dict:
    """
    Assess configured quality rules, allocate eligible water,
    and calculate estimated impact.

    Each demand's name must have a corresponding entry in
    rules_by_use. Missing rule configurations are not eligible.
    """

    eligibility = {}

    for demand in demands:
        eligibility[demand.name] = assess_use(
            measurements=measurements,
            required_rules=rules_by_use.get(demand.name, []),
        )

    assessed_demands = [
        WaterDemand(
            name=demand.name,
            demand_litres=demand.demand_litres,
            priority=demand.priority,
            compatible=(
                demand.compatible
                and eligibility[demand.name]["eligible"]
            ),
        )
        for demand in demands
    ]

    allocations = allocate_water(
        available_litres=available_litres,
        demands=assessed_demands,
    )

    total_allocated = sum(
        allocation.allocated_litres
        for allocation in allocations
    )

    impact = calculate_impact(
        total_reused_litres=total_allocated,
        freshwater_cost_per_1000_litres=(
            freshwater_cost_per_1000_litres
        ),
    )

    return {
        "quality_assessments": eligibility,
        "allocations": [
            {
                "name": allocation.name,
                "demand_litres": allocation.demand_litres,
                "allocated_litres": allocation.allocated_litres,
                "status": allocation.status,
            }
            for allocation in allocations
        ],
        "total_allocated_litres": total_allocated,
        "remaining_litres": available_litres - total_allocated,
        "impact": impact,
    }