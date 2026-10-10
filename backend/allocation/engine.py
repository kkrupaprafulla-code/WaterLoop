from dataclasses import dataclass


@dataclass
class WaterDemand:
    name: str
    demand_litres: float
    priority: int
    compatible: bool


@dataclass
class WaterAllocation:
    name: str
    demand_litres: float
    allocated_litres: float
    status: str


def allocate_water(
    available_litres: float,
    demands: list[WaterDemand]
) -> list[WaterAllocation]:

    if available_litres < 0:
        raise ValueError("Available water cannot be negative.")

    for demand in demands:
        if demand.demand_litres < 0:
            raise ValueError("Water demand cannot be negative.")

    remaining = available_litres
    results = []

    eligible_demands = sorted(
        demands,
        key=lambda item: (-item.priority, item.name)
    )

    for demand in eligible_demands:
        if not demand.compatible:
            allocated = 0.0
            status = "NOT_ELIGIBLE"

        else:
            allocated = min(
                demand.demand_litres,
                remaining
            )

            remaining -= allocated

            if allocated == demand.demand_litres:
                status = "FULL"
            elif allocated > 0:
                status = "PARTIAL"
            else:
                status = "UNALLOCATED"

        results.append(
            WaterAllocation(
                name=demand.name,
                demand_litres=demand.demand_litres,
                allocated_litres=allocated,
                status=status
            )
        )

    return results